from datetime import date, timedelta

from fastapi import APIRouter, Query, Request

from schemas import ActivityDay, ActivitySummary, ActivityResponse
from user_dep import get_oura

router = APIRouter(prefix="/api")


@router.get("/activity", response_model=ActivityResponse)
async def get_activity(request: Request, days: int = Query(default=7, ge=0, le=2200), user: str = Query(default="cody")):
    effective = days if days > 0 else 2200
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=effective)).isoformat()

    oura = get_oura(request, user)
    raw = await oura.fetch("/v2/usercollection/daily_activity", start_date, end_date)

    daily = []
    for record in raw:
        high_sec = record.get("high_activity_time", 0) or 0
        med_sec = record.get("medium_activity_time", 0) or 0
        low_sec = record.get("low_activity_time", 0) or 0

        daily.append(ActivityDay(
            day=record.get("day", ""),
            score=record.get("score"),
            active_calories=record.get("active_calories"),
            total_calories=record.get("total_calories"),
            steps=record.get("steps"),
            high_activity_time=round(high_sec / 60, 1),
            medium_activity_time=round(med_sec / 60, 1),
            low_activity_time=round(low_sec / 60, 1),
            equivalent_walking_distance=record.get("equivalent_walking_distance"),
        ))

    daily.sort(key=lambda d: d.day)

    scores = [d.score for d in daily if d.score is not None]
    steps_list = [d.steps for d in daily if d.steps is not None]
    cals = [d.active_calories for d in daily if d.active_calories is not None]
    active_mins = [
        (d.high_activity_time or 0) + (d.medium_activity_time or 0) + (d.low_activity_time or 0)
        for d in daily
    ]

    summary = ActivitySummary(
        avg_score=round(sum(scores) / len(scores), 1) if scores else None,
        total_steps=sum(steps_list),
        avg_calories=round(sum(cals) / len(cals), 1) if cals else None,
        total_active_minutes=round(sum(active_mins), 1),
    )

    return ActivityResponse(summary=summary, daily=daily)
