# Configuration Management
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Smart Learning AI Service"
    DEBUG: bool = True

    # Spark AI - Pro版本 (用于拍照搜题)
    SPARK_APP_ID: str = ""
    SPARK_API_KEY: str = ""
    SPARK_API_SECRET: str = ""
    SPARK_MODEL_VERSION: str = "v3.0"

    # Spark AI - Lite版本 (用于AI答疑)
    SPARK_LITE_APP_ID: str = ""
    SPARK_LITE_API_KEY: str = ""
    SPARK_LITE_API_SECRET: str = ""

    # OCR
    OCR_APP_ID: str = ""
    OCR_API_KEY: str = ""
    OCR_API_SECRET: str = ""
    OCR_HANDWRITING_APP_ID: str = ""
    OCR_HANDWRITING_API_KEY: str = ""

    # MySQL
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DATABASE: str = "smart_learning"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    # Cache TTL (seconds)
    CACHE_AI_RESPONSE_TTL: int = 86400  # 24h
    CACHE_REPORT_TTL: int = 3600        # 1h
    CACHE_USER_STATS_TTL: int = 300     # 5min

    # Rate Limit
    RATE_LIMIT_REQUESTS: int = 10
    RATE_LIMIT_WINDOW: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
