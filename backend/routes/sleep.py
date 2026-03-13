import asyncio
from datetime import date, timedelta

from fastapi import APIRouter, Query, Request

from schemas import SleepDay, SleepSummary, SleepResponse

router = APIRouter(prefix="/api")


@router.get("/sleep", response_model=SleepResponse)
async def get_sleep(request: Request, days: int = Query(default=7, ge=0, le=2200)):
    effective = days if days > 0 else 2200
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=effective)).isoformat()

    oura = request.app.state.oura

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

    daily = []
    for record in raw:
        day = record.get("day", "")
        # Oura returns durations in seconds for sleep periods
        total_seconds = record.get("total_sleep_duration", 0) or 0
        rem_seconds = record.get("rem_sleep_duration", 0) or 0
        deep_seconds = record.get("deep_sleep_duration", 0) or 0
        light_seconds = record.get("light_sleep_duration", 0) or 0
        latency_seconds = record.get("latency", 0) or record.get("sleep_onset_latency", 0) or 0

        # Get score and contributors from daily_sleep endpoint
        contribs = contributor_by_day.get(day, {})

        daily.append(SleepDay(
            day=day,
            score=score_by_day.get(day),
            deep_sleep=round(deep_seconds / 60, 1),
            rem_sleep=round(rem_seconds / 60, 1),
            light_sleep=round(light_seconds / 60, 1),
            total_sleep=round(total_seconds / 60, 1),
            efficiency=record.get("efficiency"),
            latency=round(latency_seconds / 60, 1),
            timing=contribs.get("timing"),
            restfulness=contribs.get("restfulness"),
        ))

    # Sort by date
    daily.sort(key=lambda d: d.day)

    # Compute summary
    scores = [d.score for d in daily if d.score is not None]
    efficiencies = [d.efficiency for d in daily if d.efficiency is not None]

    summary = SleepSummary(
        avg_score=round(sum(scores) / len(scores), 1) if scores else None,
        avg_efficiency=round(sum(efficiencies) / len(efficiencies), 1) if efficiencies else None,
        total_nights=len(daily),
    )

    return SleepResponse(summary=summary, daily=daily)
