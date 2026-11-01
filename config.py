from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
class Settings(BaseSettings):
    app_name: str = "AgriVision AI API"
    database_url: str = f"sqlite:///{BASE_DIR / 'agrivision.db'}"
    upload_dir: str = str(BASE_DIR / "uploads")
    max_upload_mb: int = 8
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"
    weather_api_key: str | None = None
    disease_model_path: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    @property
    def cors_origins(self): return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]
settings = Settings()
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
