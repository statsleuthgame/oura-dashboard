from fastapi import APIRouter, Query, Request

from apple_health_db import get_connection, query_parse_status
from apple_health_schemas import AppleParseStatusResponse
from user_dep import get_user_key

router = APIRouter(prefix="/api")


@router.get("/apple/parse/status", response_model=AppleParseStatusResponse)
async def get_parse_status(request: Request, user: str = Query(default="cody")):
    key = get_user_key(request, user)
    profile = request.app.state.users[key]
    db = profile["apple_db"]

    if db is None:
        return AppleParseStatusResponse(status="not_started")

    try:
        result = query_parse_status(db)
        return AppleParseStatusResponse(**result)
    except Exception:
        return AppleParseStatusResponse(status="not_started")
