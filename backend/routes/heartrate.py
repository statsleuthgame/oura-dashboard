from collections import defaultdict
from datetime import date, timedelta

from fastapi import APIRouter, Query, Request

from schemas import HeartRatePoint, HeartRateResponse

router = APIRouter(prefix="/api")


@router.get("/heartrate", response_model=HeartRateResponse)
async def get_heartrate(request: Request, days: int = Query(default=7, ge=1, le=90)):
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=days)).isoformat()

    raw = await request.app.state.oura.fetch(
        "/v2/usercollection/heartrate", start_date, end_date
    )

    if not raw:
        return HeartRateResponse(data=[])

    # Downsample based on range
    if days <= 7:
        # Hourly averages
        buckets: dict[str, list[int]] = defaultdict(list)
        for point in raw:
            ts = point.get("timestamp", "")
            bpm = point.get("bpm")
            if bpm is None:
                continue
            # Truncate to hour: "2024-01-15T14:xx:xx" -> "2024-01-15T14:00:00"
            hour_key = ts[:13] + ":00:00"
            buckets[hour_key].append(bpm)

        data = [
            HeartRatePoint(timestamp=k, bpm=round(sum(v) / len(v)))
            for k, v in sorted(buckets.items())
        ]
    else:
        # Daily averages
        buckets: dict[str, list[int]] = defaultdict(list)
        for point in raw:
            ts = point.get("timestamp", "")
            bpm = point.get("bpm")
            if bpm is None:
                continue
            day_key = ts[:10]
            buckets[day_key].append(bpm)

        data = [
            HeartRatePoint(timestamp=k, bpm=round(sum(v) / len(v)))
            for k, v in sorted(buckets.items())
        ]

    return HeartRateResponse(data=data)
