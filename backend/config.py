from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    oura_api_token: str
    oura_base_url: str = "https://api.ouraring.com"
    apple_health_export_path: str = "../apple_health_export/export.xml"
    apple_health_db_path: str = "./apple_health.db"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
