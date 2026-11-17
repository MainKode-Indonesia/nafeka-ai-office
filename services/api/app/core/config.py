from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Nafeka AI Office API"
    app_version: str = "0.2.0"
    app_env: str = "development"
    debug: bool = False
    database_url: str

    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    cors_origins: str = "http://localhost:3000"

    login_rate_limit_attempts: int = Field(default=5, ge=1, le=20)
    login_rate_limit_window_minutes: int = Field(default=15, ge=1, le=1440)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
