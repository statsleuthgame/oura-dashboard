from fastapi import APIRouter, Query, Request, HTTPException

from apple_health_db import query_daily_sleep
from apple_health_schemas import AppleSleepDay, AppleSleepSummary, AppleSleepResponse

router = APIRouter(prefix="/api")


@router.get("/apple/sleep", response_model=AppleSleepResponse)
async def get_apple_sleep(request: Request, days: int = Query(default=30, ge=0, le=2200)):
    db = request.app.state.apple_db
    if db is None:
        raise HTTPException(status_code=503, detail="Apple Health data is being parsed. Check /api/apple/parse/status")

    rows = query_daily_sleep(db, days)
    daily = [AppleSleepDay(**r) for r in rows]

    totals = [d.total_sleep for d in daily if d.total_sleep > 0]
    deeps = [d.deep for d in daily if d.deep > 0]
    rems = [d.rem for d in daily if d.rem > 0]

    summary = AppleSleepSummary(
        avg_total_sleep=round(sum(totals) / len(totals), 1) if totals else None,
        avg_deep=round(sum(deeps) / len(deeps), 1) if deeps else None,
        avg_rem=round(sum(rems) / len(rems), 1) if rems else None,
        total_nights=len(daily),
    )
    return AppleSleepResponse(summary=summary, daily=daily)
