from datetime import date, timedelta

from fastapi import APIRouter, Query, Request

from schemas import ReadinessDay, ReadinessSummary, ReadinessResponse
from user_dep import get_oura

router = APIRouter(prefix="/api")


@router.get("/readiness", response_model=ReadinessResponse)
async def get_readiness(request: Request, days: int = Query(default=7, ge=0, le=2200), user: str = Query(default="cody")):
    effective = days if days > 0 else 2200
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=effective)).isoformat()

    oura = get_oura(request, user)
    raw = await oura.fetch("/v2/usercollection/daily_readiness", start_date, end_date)

    daily = []
    for record in raw:
        contributors = record.get("contributors", {})
        daily.append(ReadinessDay(
            day=record.get("day", ""),
            score=record.get("score"),
            temperature_deviation=record.get("temperature_deviation"),
            hrv_balance=contributors.get("hrv_balance"),
            resting_heart_rate=contributors.get("resting_heart_rate"),
            body_temperature=contributors.get("body_temperature"),
            recovery_index=contributors.get("recovery_index"),
            sleep_balance=contributors.get("sleep_balance"),
            activity_balance=contributors.get("activity_balance"),
        ))

    daily.sort(key=lambda d: d.day)

    scores = [d.score for d in daily if d.score is not None]
    hrv_vals = [d.hrv_balance for d in daily if d.hrv_balance is not None]
    hr_vals = [d.resting_heart_rate for d in daily if d.resting_heart_rate is not None]

    summary = ReadinessSummary(
        avg_score=round(sum(scores) / len(scores), 1) if scores else None,
        avg_hrv_balance=round(sum(hrv_vals) / len(hrv_vals), 1) if hrv_vals else None,
        avg_resting_hr=round(sum(hr_vals) / len(hr_vals), 1) if hr_vals else None,
    )

    return ReadinessResponse(summary=summary, daily=daily)
