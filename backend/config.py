from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class UserConfig:
    def __init__(self, key: str, name: str, oura_token: str, db_path: str, xml_path: str):
        self.key = key
        self.name = name
        self.oura_token = oura_token
        self.db_path = db_path
        self.xml_path = xml_path


class Settings(BaseSettings):
    oura_base_url: str = "https://api.ouraring.com"
    anthropic_api_key: str = ""

    # User: Cody
    cody_oura_token: str = ""
    cody_apple_health_db: str = "./apple_health_cody.db"
    cody_apple_health_xml: str = "../apple_health_export/export.xml"

    # User: Stef
    stef_oura_token: str = ""
    stef_apple_health_db: str = "./apple_health_stef.db"
    stef_apple_health_xml: str = "../apple_health_export_stef/export.xml"

    # Legacy fallback
    oura_api_token: str = ""
    apple_health_db_path: str = "./apple_health.db"
    apple_health_export_path: str = "../apple_health_export/export.xml"

    model_config = SettingsConfigDict(env_file=".env")

    def get_users(self) -> list[UserConfig]:
        users = []
        if self.cody_oura_token:
            users.append(UserConfig("cody", "Cody", self.cody_oura_token, self.cody_apple_health_db, self.cody_apple_health_xml))
        elif self.oura_api_token:
            # Legacy single-user fallback
            users.append(UserConfig("cody", "Cody", self.oura_api_token, self.apple_health_db_path, self.apple_health_export_path))
        if self.stef_oura_token:
            users.append(UserConfig("stef", "Stef", self.stef_oura_token, self.stef_apple_health_db, self.stef_apple_health_xml))
        return users


@lru_cache
def get_settings() -> Settings:
    return Settings()
