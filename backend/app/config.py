from datetime import time

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "gencontrol"
    DB_USERNAME: str = "gencontrol_user"
    DB_PASSWORD: str

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_TTL_SECONDS: int = 3600

    # Server
    SERVER_PORT: int = 8080
    APP_BASE_URL: str = "http://localhost:8080"

    # JWT
    JWT_SECRET: str
    JWT_EXPIRATION_MS: int = 86400000

    # First admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str
    ADMIN_FULLNAME: str = "Системний Адміністратор"

    # Google Sheets (future)
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = ""
    GOOGLE_SHEETS_SPREADSHEET_ID: str = ""

    # App rules — формат HH:MM, валідується нижче
    DEFAULT_WORK_TIME_START: str = "07:00"
    DEFAULT_WORK_TIME_END: str = "22:00"

    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # --- Валідатори ---

    @field_validator("DEFAULT_WORK_TIME_START", "DEFAULT_WORK_TIME_END", mode="before")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        try:
            parts = v.split(":")
            if len(parts) != 2:
                raise ValueError
            h, m = int(parts[0]), int(parts[1])
            time(h, m)  # кине ValueError якщо години/хвилини поза діапазоном
        except (ValueError, AttributeError) as exc:
            raise ValueError(
                f"Невірний формат часу '{v}'. Очікується HH:MM (наприклад, 07:00)."
            ) from exc
        return v

    # --- Властивості ---

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def redis_url(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def jwt_expiration_seconds(self) -> int:
        return self.JWT_EXPIRATION_MS // 1000

    @property
    def work_time_start(self) -> time:
        h, m = self.DEFAULT_WORK_TIME_START.split(":")
        return time(int(h), int(m))

    @property
    def work_time_end(self) -> time:
        h, m = self.DEFAULT_WORK_TIME_END.split(":")
        return time(int(h), int(m))


settings = Settings()
