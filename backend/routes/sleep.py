import asyncio
from datetime import date, timedelta

from fastapi import APIRouter, Query, Request

from schemas import SleepDay, SleepSummary, SleepResponse
from user_dep import get_oura

router = APIRouter(prefix="/api")


@router.get("/sleep", response_model=SleepResponse)
async def get_sleep(request: Request, days: int = Query(default=7, ge=0, le=2200), user: str = Query(default="cody")):
    effective = days if days > 0 else 2200
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=effective)).isoformat()

    oura = get_oura(request, user)

    # Fetch both endpoints: sleep periods (durations) and daily_sleep (scores)
    raw, daily_scores_raw = await asyncio.gather(
        oura.fetch("/v2/usercollection/sleep", start_date, end_date),
        oura.fetch("/v2/usercollection/daily_sleep", start_date, end_date),
    )

    # Build score lookup by day
    score_by_day = {}
    contributor_by_day = {}
    for rec in daily_scores_raw:
        day = rec.get("day", "")
        if day:
            score_by_day[day] = rec.get("score")
            contributor_by_day[day] = rec.get("contributors", {})

    # Aggregate multiple sleep records per day (main sleep + naps)
    by_day: dict[str, dict] = {}
    for record in raw:
        day = record.get("day", "")
        if not day:
            continue
        total_seconds = record.get("total_sleep_duration", 0) or 0
        rem_seconds = record.get("rem_sleep_duration", 0) or 0
        deep_seconds = record.get("deep_sleep_duration", 0) or 0
        light_seconds = record.get("light_sleep_duration", 0) or 0
        latency_seconds = record.get("latency", 0) or record.get("sleep_onset_latency", 0) or 0

        if day not in by_day:
            by_day[day] = {"deep": 0, "rem": 0, "light": 0, "total": 0, "efficiency": None, "latency": 0}

        by_day[day]["deep"] += deep_seconds
        by_day[day]["rem"] += rem_seconds
        by_day[day]["light"] += light_seconds
        by_day[day]["total"] += total_seconds
        by_day[day]["latency"] += latency_seconds
        # Keep efficiency from the longest sleep period
        if total_seconds > 0 and (by_day[day]["efficiency"] is None or total_seconds > by_day[day].get("max_dur", 0)):
            by_day[day]["efficiency"] = record.get("efficiency")
            by_day[day]["max_dur"] = total_seconds

    daily = []
    for day in sorted(by_day):
        d = by_day[day]
        contribs = contributor_by_day.get(day, {})
        daily.append(SleepDay(
            day=day,
            score=score_by_day.get(day),
            deep_sleep=round(d["deep"] / 60, 1),
            rem_sleep=round(d["rem"] / 60, 1),
            light_sleep=round(d["light"] / 60, 1),
            total_sleep=round(d["total"] / 60, 1),
            efficiency=d["efficiency"],
            latency=round(d["latency"] / 60, 1),
            timing=contribs.get("timing"),
            restfulness=contribs.get("restfulness"),
        ))

    scores = [d.score for d in daily if d.score is not None]
    efficiencies = [d.efficiency for d in daily if d.efficiency is not None]

    summary = SleepSummary(
        avg_score=round(sum(scores) / len(scores), 1) if scores else None,
        avg_efficiency=round(sum(efficiencies) / len(efficiencies), 1) if efficiencies else None,
        total_nights=len(daily),
    )

    return SleepResponse(summary=summary, daily=daily)
