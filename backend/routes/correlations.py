import asyncio
from datetime import date, timedelta

import numpy as np
from fastapi import APIRouter, Query, Request

from schemas import CorrelationPair, CorrelationsResponse
from apple_health_db import (
    query_daily_heart_rate, query_daily_hrv, query_daily_resting_hr,
    query_daily_steps, query_daily_energy,
)

router = APIRouter(prefix="/api")

METRIC_KEYS = [
    "sleep_score", "total_sleep", "deep_sleep", "efficiency",
    "readiness_score", "hrv_balance", "resting_heart_rate",
    "activity_score", "steps", "active_calories",
    "apple_avg_hr", "apple_hrv", "apple_resting_hr",
    "apple_steps", "apple_active_cal",
]


@router.get("/correlations", response_model=CorrelationsResponse)
async def get_correlations(request: Request, days: int = Query(default=30, ge=0, le=2200), user: str = Query(default="cody")):
    from user_dep import get_oura, get_user_key
    oura_days = days if days > 0 else 2200
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=oura_days)).isoformat()

    oura = get_oura(request, user)

    # Fetch Oura datasets in parallel
    sleep_data, readiness_data, activity_data = await asyncio.gather(
        oura.fetch("/v2/usercollection/sleep", start_date, end_date),
        oura.fetch("/v2/usercollection/daily_readiness", start_date, end_date),
        oura.fetch("/v2/usercollection/daily_activity", start_date, end_date),
    )

    # Build dict keyed by day
    by_day: dict[str, dict] = {}

    for record in sleep_data:
        day = record.get("day", "")
        if not day:
            continue
        by_day.setdefault(day, {})
        total_sec = record.get("total_sleep_duration", 0) or 0
        deep_sec = record.get("deep_sleep_duration", 0) or 0
        by_day[day]["sleep_score"] = record.get("score")
        by_day[day]["total_sleep"] = round(total_sec / 60, 1)
        by_day[day]["deep_sleep"] = round(deep_sec / 60, 1)
        by_day[day]["efficiency"] = record.get("efficiency")

    for record in readiness_data:
        day = record.get("day", "")
        if not day:
            continue
        by_day.setdefault(day, {})
        contributors = record.get("contributors", {})
        by_day[day]["readiness_score"] = record.get("score")
        by_day[day]["hrv_balance"] = contributors.get("hrv_balance")
        by_day[day]["resting_heart_rate"] = contributors.get("resting_heart_rate")

    for record in activity_data:
        day = record.get("day", "")
        if not day:
            continue
        by_day.setdefault(day, {})
        by_day[day]["activity_score"] = record.get("score")
        by_day[day]["steps"] = record.get("steps")
        by_day[day]["active_calories"] = record.get("active_calories")

    # Add Apple Health data if available
    key = get_user_key(request, user)
    apple_db = request.app.state.users[key]["apple_db"]
    if apple_db is not None:
        apple_days = days

        for row in query_daily_heart_rate(apple_db, apple_days):
            day = row["day"]
            by_day.setdefault(day, {})
            by_day[day]["apple_avg_hr"] = row.get("avg_hr")

        for row in query_daily_hrv(apple_db, apple_days):
            day = row["day"]
            by_day.setdefault(day, {})
            by_day[day]["apple_hrv"] = row.get("avg_hrv")

        for row in query_daily_resting_hr(apple_db, apple_days):
            day = row["day"]
            by_day.setdefault(day, {})
            by_day[day]["apple_resting_hr"] = row.get("resting_hr")

        for row in query_daily_steps(apple_db, apple_days):
            day = row["day"]
            by_day.setdefault(day, {})
            by_day[day]["apple_steps"] = row.get("steps")

        for row in query_daily_energy(apple_db, apple_days):
            day = row["day"]
            by_day.setdefault(day, {})
            by_day[day]["apple_active_cal"] = row.get("active_cal")

    # Compute correlations
    active_keys = METRIC_KEYS if apple_db is not None else METRIC_KEYS[:10]
    pairs: list[CorrelationPair] = []
    matrix: dict[str, dict[str, float | None]] = {k: {} for k in active_keys}

    for i, key_a in enumerate(active_keys):
        for j, key_b in enumerate(active_keys):
            if j <= i:
                if i == j:
                    matrix[key_a][key_b] = 1.0
                continue

            vals_a = []
            vals_b = []
            for day_data in by_day.values():
                a = day_data.get(key_a)
                b = day_data.get(key_b)
                if a is not None and b is not None:
                    vals_a.append(float(a))
                    vals_b.append(float(b))

            n = len(vals_a)
            if n < 5:
                matrix[key_a][key_b] = None
                matrix[key_b][key_a] = None
                continue

            arr_a = np.array(vals_a)
            arr_b = np.array(vals_b)

            if np.std(arr_a) == 0 or np.std(arr_b) == 0:
                matrix[key_a][key_b] = None
                matrix[key_b][key_a] = None
                continue

            r = float(np.corrcoef(arr_a, arr_b)[0, 1])
            r_rounded = round(r, 3)

            matrix[key_a][key_b] = r_rounded
            matrix[key_b][key_a] = r_rounded

            pairs.append(CorrelationPair(
                metric_a=key_a,
                metric_b=key_b,
                r=r_rounded,
                n=n,
            ))

    pairs.sort(key=lambda p: abs(p.r), reverse=True)

    return CorrelationsResponse(pairs=pairs, matrix=matrix)
