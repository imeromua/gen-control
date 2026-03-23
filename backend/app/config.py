from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "gencontrol"
    DB_USERNAME: str = "gencontrol_user"
    DB_PASSWORD: str = "supersecretpassword"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_TTL_SECONDS: int = 3600

    # Server
    SERVER_PORT: int = 8080
    APP_BASE_URL: str = "http://localhost:8080"

    # JWT
    JWT_SECRET: str = "your-very-long-secret-key-here"
    JWT_EXPIRATION_MS: int = 86400000

    # First admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "changeme123"
    ADMIN_FULLNAME: str = "Системний Адміністратор"

    # Google Sheets (future)
    GOOGLE_SHEETS_CREDENTIALS_PATH: str = ""
    GOOGLE_SHEETS_SPREADSHEET_ID: str = ""

    # App rules
    DEFAULT_WORK_TIME_START: str = "07:00"
    DEFAULT_WORK_TIME_END: str = "22:00"

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


settings = Settings()
