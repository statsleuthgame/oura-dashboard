from fastapi import APIRouter, Query, Request

from apple_health_db import query_daily_respiratory, query_daily_spo2
from apple_health_schemas import (
    AppleRespiratoryDay, AppleRespiratorySummary, AppleRespiratoryResponse,
    AppleSpo2Day, AppleSpo2Summary, AppleSpo2Response,
)
from user_dep import get_apple_db

router = APIRouter(prefix="/api")


@router.get("/apple/respiratory", response_model=AppleRespiratoryResponse)
async def get_apple_respiratory(request: Request, days: int = Query(default=30, ge=0, le=2200), user: str = Query(default="cody")):
    conn = get_apple_db(request, user)
    rows = query_daily_respiratory(conn, days)
    daily = [AppleRespiratoryDay(day=r["day"], avg_rate=round(r["avg_rate"], 1)) for r in rows]

    rates = [d.avg_rate for d in daily if d.avg_rate is not None]
    summary = AppleRespiratorySummary(
        avg_respiratory_rate=round(sum(rates) / len(rates), 1) if rates else None,
        total_days=len(daily),
    )
    return AppleRespiratoryResponse(summary=summary, daily=daily)


@router.get("/apple/spo2", response_model=AppleSpo2Response)
async def get_apple_spo2(request: Request, days: int = Query(default=30, ge=0, le=2200), user: str = Query(default="cody")):
    conn = get_apple_db(request, user)
    rows = query_daily_spo2(conn, days)
    daily = [AppleSpo2Day(day=r["day"], avg_spo2=round(r["avg_spo2"], 1), min_spo2=round(r["min_spo2"], 1)) for r in rows]

    avgs = [d.avg_spo2 for d in daily if d.avg_spo2 is not None]
    mins = [d.min_spo2 for d in daily if d.min_spo2 is not None]
    summary = AppleSpo2Summary(
        avg_spo2=round(sum(avgs) / len(avgs), 1) if avgs else None,
        min_spo2=min(mins) if mins else None,
        total_days=len(daily),
    )
    return AppleSpo2Response(summary=summary, daily=daily)
