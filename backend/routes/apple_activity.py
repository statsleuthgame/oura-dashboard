from fastapi import APIRouter, Query, Request

from apple_health_db import query_daily_steps, query_daily_energy
from apple_health_schemas import (
    AppleStepsDay, AppleStepsSummary, AppleStepsResponse,
    AppleEnergyDay, AppleEnergySummary, AppleEnergyResponse,
)
from user_dep import get_apple_db

router = APIRouter(prefix="/api")


@router.get("/apple/steps", response_model=AppleStepsResponse)
async def get_apple_steps(request: Request, days: int = Query(default=30, ge=0, le=2200), user: str = Query(default="cody")):
    conn = get_apple_db(request, user)
    rows = query_daily_steps(conn, days)
    daily = [AppleStepsDay(**r) for r in rows]

    steps_list = [d.steps for d in daily if d.steps > 0]
    dist_list = [d.distance for d in daily if d.distance > 0]
    summary = AppleStepsSummary(
        avg_daily_steps=round(sum(steps_list) / len(steps_list), 1) if steps_list else None,
        total_steps=sum(steps_list),
        avg_distance=round(sum(dist_list) / len(dist_list), 2) if dist_list else None,
        total_flights=sum(d.flights for d in daily),
    )
    return AppleStepsResponse(summary=summary, daily=daily)


@router.get("/apple/energy", response_model=AppleEnergyResponse)
async def get_apple_energy(request: Request, days: int = Query(default=30, ge=0, le=2200), user: str = Query(default="cody")):
    conn = get_apple_db(request, user)
    rows = query_daily_energy(conn, days)
    daily = [AppleEnergyDay(**r) for r in rows]

    active = [d.active_cal for d in daily if d.active_cal > 0]
    basal = [d.basal_cal for d in daily if d.basal_cal > 0]
    total = [d.total_cal for d in daily if d.total_cal > 0]
    summary = AppleEnergySummary(
        avg_active_cal=round(sum(active) / len(active), 1) if active else None,
        avg_basal_cal=round(sum(basal) / len(basal), 1) if basal else None,
        avg_total_cal=round(sum(total) / len(total), 1) if total else None,
        total_calories=round(sum(total)),
    )
    return AppleEnergyResponse(summary=summary, daily=daily)
