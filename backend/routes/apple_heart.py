from fastapi import APIRouter, Query, Request, HTTPException

from apple_health_db import query_daily_heart_rate, query_daily_hrv, query_daily_resting_hr
from apple_health_schemas import (
    AppleHeartRateDay, AppleHeartRateSummary, AppleHeartRateResponse,
    AppleHrvDay, AppleHrvSummary, AppleHrvResponse,
    AppleRestingHrDay, AppleRestingHrSummary, AppleRestingHrResponse,
)

router = APIRouter(prefix="/api")


def _get_db(request: Request):
    db = request.app.state.apple_db
    if db is None:
        raise HTTPException(status_code=503, detail="Apple Health data is being parsed. Check /api/apple/parse/status")
    return db


@router.get("/apple/heart-rate", response_model=AppleHeartRateResponse)
async def get_apple_heart_rate(request: Request, days: int = Query(default=30, ge=0, le=2200)):
    conn = _get_db(request)
    rows = query_daily_heart_rate(conn, days)
    daily = [AppleHeartRateDay(day=r["day"], avg_hr=round(r["avg_hr"], 1), min_hr=round(r["min_hr"]), max_hr=round(r["max_hr"])) for r in rows]

    avg_hrs = [d.avg_hr for d in daily if d.avg_hr is not None]
    summary = AppleHeartRateSummary(
        avg_hr=round(sum(avg_hrs) / len(avg_hrs), 1) if avg_hrs else None,
        min_hr=min((d.min_hr for d in daily if d.min_hr is not None), default=None),
        max_hr=max((d.max_hr for d in daily if d.max_hr is not None), default=None),
        total_days=len(daily),
    )
    return AppleHeartRateResponse(summary=summary, daily=daily)


@router.get("/apple/hrv", response_model=AppleHrvResponse)
async def get_apple_hrv(request: Request, days: int = Query(default=30, ge=0, le=2200)):
    conn = _get_db(request)
    rows = query_daily_hrv(conn, days)
    daily = [AppleHrvDay(day=r["day"], avg_hrv=round(r["avg_hrv"], 1), min_hrv=round(r["min_hrv"], 1), max_hrv=round(r["max_hrv"], 1)) for r in rows]

    avg_hrvs = [d.avg_hrv for d in daily if d.avg_hrv is not None]
    summary = AppleHrvSummary(
        avg_hrv=round(sum(avg_hrvs) / len(avg_hrvs), 1) if avg_hrvs else None,
        total_days=len(daily),
    )
    return AppleHrvResponse(summary=summary, daily=daily)


@router.get("/apple/resting-hr", response_model=AppleRestingHrResponse)
async def get_apple_resting_hr(request: Request, days: int = Query(default=30, ge=0, le=2200)):
    conn = _get_db(request)
    rows = query_daily_resting_hr(conn, days)
    daily = [AppleRestingHrDay(day=r["day"], resting_hr=round(r["resting_hr"], 1)) for r in rows]

    vals = [d.resting_hr for d in daily if d.resting_hr is not None]
    summary = AppleRestingHrSummary(
        avg_resting_hr=round(sum(vals) / len(vals), 1) if vals else None,
        total_days=len(daily),
    )
    return AppleRestingHrResponse(summary=summary, daily=daily)
