from fastapi import Query, Request, HTTPException

from oura_client import OuraClient


def get_user_key(request: Request, user: str = Query(default="cody")) -> str:
    if user not in request.app.state.users:
        raise HTTPException(status_code=404, detail=f"User '{user}' not found")
    return user


def get_oura(request: Request, user: str = Query(default="cody")) -> OuraClient:
    key = get_user_key(request, user)
    return request.app.state.users[key]["oura"]


def get_apple_db(request: Request, user: str = Query(default="cody")):
    key = get_user_key(request, user)
    db = request.app.state.users[key]["apple_db"]
    if db is None:
        raise HTTPException(status_code=503, detail="Apple Health data is being parsed. Check /api/apple/parse/status")
    return db
