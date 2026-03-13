from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from oura_client import OuraClient
from routes import sleep, readiness, activity, heartrate, correlations


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.oura = OuraClient(
        token=settings.oura_api_token,
        base_url=settings.oura_base_url,
    )
    yield
    await app.state.oura.close()


app = FastAPI(title="Oura Dashboard API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(sleep.router)
app.include_router(readiness.router)
app.include_router(activity.router)
app.include_router(heartrate.router)
app.include_router(correlations.router)
