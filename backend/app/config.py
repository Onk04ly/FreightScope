from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    hf_api_key: str = ""
    db_url: str = "postgresql+asyncpg://freightscope:freightscope@localhost:5432/freightscope"
    redis_url: str = "redis://localhost:6379/0"
    openweather_api_key: str = ""
    upload_dir: str = "uploads"


settings = Settings()
