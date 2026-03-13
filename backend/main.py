import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from oura_client import OuraClient
from apple_health_parser import parse_export, is_parsed
from apple_health_db import get_connection
from routes import sleep, readiness, activity, heartrate, correlations
from routes import apple_heart, apple_activity, apple_sleep, apple_workouts, apple_vitals, apple_parse, insights

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Oura client
    app.state.oura = OuraClient(
        token=settings.oura_api_token,
        base_url=settings.oura_base_url,
    )

    # Apple Health DB
    app.state.apple_db = None
    db_path = settings.apple_health_db_path
    xml_path = settings.apple_health_export_path

    if is_parsed(db_path):
        logger.info("Apple Health DB found, loading...")
        app.state.apple_db = get_connection(db_path)
    elif Path(xml_path).exists():
        logger.info("Apple Health export found, parsing in background...")

        def _parse():
            parse_export(xml_path, db_path)
            app.state.apple_db = get_connection(db_path)
            logger.info("Apple Health DB ready")

        thread = threading.Thread(target=_parse, daemon=True)
        thread.start()
    else:
        logger.warning(f"No Apple Health export found at {xml_path}")

    yield
    await app.state.oura.close()
    if app.state.apple_db is not None:
        app.state.apple_db.close()


app = FastAPI(title="Health Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Oura routes
app.include_router(sleep.router)
app.include_router(readiness.router)
app.include_router(activity.router)
app.include_router(heartrate.router)
app.include_router(correlations.router)

# Apple Health routes
app.include_router(apple_heart.router)
app.include_router(apple_activity.router)
app.include_router(apple_sleep.router)
app.include_router(apple_workouts.router)
app.include_router(apple_vitals.router)
app.include_router(apple_parse.router)

# AI Insights
app.include_router(insights.router)
