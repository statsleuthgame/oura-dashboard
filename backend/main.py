import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import get_settings
from oura_client import OuraClient
from apple_health_parser import parse_export, is_parsed
from apple_health_db import get_connection
from routes import sleep, readiness, activity, correlations
from routes import apple_heart, apple_activity, apple_sleep, apple_workouts, apple_vitals, apple_parse, insights

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    # Multi-user setup
    app.state.users = {}
    for user_cfg in settings.get_users():
        oura = OuraClient(token=user_cfg.oura_token, base_url=settings.oura_base_url)
        apple_db = None
        db_path = user_cfg.db_path
        xml_path = user_cfg.xml_path

        if is_parsed(db_path):
            logger.info(f"[{user_cfg.name}] Apple Health DB found, loading...")
            apple_db = get_connection(db_path)
        elif Path(xml_path).exists():
            logger.info(f"[{user_cfg.name}] Apple Health export found, parsing in background...")

            def _parse(xp=xml_path, dp=db_path, key=user_cfg.key):
                parse_export(xp, dp)
                app.state.users[key]["apple_db"] = get_connection(dp)
                logger.info(f"[{key}] Apple Health DB ready")

            thread = threading.Thread(target=_parse, daemon=True)
            thread.start()
        else:
            logger.warning(f"[{user_cfg.name}] No Apple Health export found at {xml_path}")

        app.state.users[user_cfg.key] = {
            "name": user_cfg.name,
            "oura": oura,
            "apple_db": apple_db,
        }

    logger.info(f"Users loaded: {list(app.state.users.keys())}")

    yield

    for profile in app.state.users.values():
        await profile["oura"].close()
        if profile["apple_db"] is not None:
            profile["apple_db"].close()


app = FastAPI(title="Health Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# User list endpoint
@app.get("/api/users")
async def list_users():
    return [{"key": k, "name": v["name"]} for k, v in app.state.users.items()]


# Oura routes
app.include_router(sleep.router)
app.include_router(readiness.router)
app.include_router(activity.router)
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

# Serve built frontend in production
STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve the React SPA for all non-API routes."""
        file_path = STATIC_DIR / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
