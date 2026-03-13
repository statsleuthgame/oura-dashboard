from datetime import date, timedelta

from fastapi import APIRouter, Query, Request

from schemas import SleepDay, SleepSummary, SleepResponse

router = APIRouter(prefix="/api")


@router.get("/sleep", response_model=SleepResponse)
async def get_sleep(request: Request, days: int = Query(default=7, ge=1, le=90)):
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()

    raw = await request.app.state.oura.fetch(
        "/v2/usercollection/sleep", start_date, end_date
    )

    daily = []
    for record in raw:
        contributors = record.get("contributors", {})
        # Oura returns durations in seconds for sleep periods
        total_seconds = record.get("total_sleep_duration", 0) or 0
        rem_seconds = record.get("rem_sleep_duration", 0) or 0
        deep_seconds = record.get("deep_sleep_duration", 0) or 0
        light_seconds = record.get("light_sleep_duration", 0) or 0
        latency_seconds = record.get("latency", 0) or record.get("sleep_onset_latency", 0) or 0

        daily.append(SleepDay(
            day=record.get("day", ""),
            score=record.get("score"),
            deep_sleep=round(deep_seconds / 60, 1),
            rem_sleep=round(rem_seconds / 60, 1),
            light_sleep=round(light_seconds / 60, 1),
            total_sleep=round(total_seconds / 60, 1),
            efficiency=record.get("efficiency"),
            latency=round(latency_seconds / 60, 1),
            timing=contributors.get("timing"),
            restfulness=contributors.get("restfulness"),
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
