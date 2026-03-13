import threading
from pathlib import Path

from fastapi import APIRouter, Request, HTTPException

from apple_health_db import get_connection, query_parse_status
from apple_health_parser import parse_export, is_parsed
from apple_health_schemas import AppleParseStatusResponse
from config import get_settings

router = APIRouter(prefix="/api")


@router.post("/apple/parse")
async def trigger_parse(request: Request):
    settings = get_settings()
    xml_path = settings.apple_health_export_path
    db_path = settings.apple_health_db_path

    if not Path(xml_path).exists():
        raise HTTPException(status_code=404, detail=f"Export file not found: {xml_path}")

    # Close existing connection
    if request.app.state.apple_db is not None:
        request.app.state.apple_db.close()
        request.app.state.apple_db = None

    # Delete existing DB
    db_file = Path(db_path)
    if db_file.exists():
        db_file.unlink()

    def _parse():
        parse_export(xml_path, db_path)
        request.app.state.apple_db = get_connection(db_path)

    thread = threading.Thread(target=_parse, daemon=True)
    thread.start()

    return {"status": "started"}


@router.get("/apple/parse/status", response_model=AppleParseStatusResponse)
async def get_parse_status(request: Request):
    settings = get_settings()
    db_path = settings.apple_health_db_path

    if not Path(db_path).exists():
        return AppleParseStatusResponse(status="not_started")

    try:
        conn = get_connection(db_path)
        result = query_parse_status(conn)
        conn.close()
        return AppleParseStatusResponse(**result)
    except Exception:
        return AppleParseStatusResponse(status="not_started")
