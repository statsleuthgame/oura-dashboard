from fastapi import APIRouter, Query, Request

from apple_health_db import query_workouts
from apple_health_schemas import (
    AppleWorkout, AppleWorkoutType, AppleWorkoutsSummary, AppleWorkoutsResponse,
)
from user_dep import get_apple_db

router = APIRouter(prefix="/api")


@router.get("/apple/workouts", response_model=AppleWorkoutsResponse)
async def get_apple_workouts(request: Request, days: int = Query(default=90, ge=0, le=2200), user: str = Query(default="cody")):
    conn = get_apple_db(request, user)
    workouts_raw, by_type_raw = query_workouts(conn, days)

    workouts = [AppleWorkout(**w) for w in workouts_raw]
    by_type = [AppleWorkoutType(**t) for t in by_type_raw]

    total_dur = sum(w.duration or 0 for w in workouts)
    total_cal = sum(w.total_energy or 0 for w in workouts)

    summary = AppleWorkoutsSummary(
        total_workouts=len(workouts),
        total_duration_min=round(total_dur / 60, 1) if total_dur else None,
        total_calories=round(total_cal, 1) if total_cal else None,
    )
    return AppleWorkoutsResponse(summary=summary, workouts=workouts, by_type=by_type)
