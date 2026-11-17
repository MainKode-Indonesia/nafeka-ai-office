from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nafeka AI Office API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    database_url: str = "postgresql+psycopg://nafeka:CHANGE_ME@127.0.0.1:5432/nafeka_ai_office"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
