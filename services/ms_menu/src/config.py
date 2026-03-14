from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASS: str
    REDIS_HOST: str
    REDIS_PORT: int
    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str

    @property
    def DATABASE_URL(self):
        # PSQL
        # dialect+DBAPI(driver)://user:pass@host:port/dbname
        # postgresql+asyncpg://user:pass@host:port/dbname
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def RABBITMQ_URL(self):
        # amqp://user:pass@host:port/
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/"

    @property
    def REDIS_URL(self):
        # REDIS_URL = "redis://cache:6379/0"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/0"

    @property
    def MINIO_URL(self):
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"

    @property
    def MINIO_ACCESS_KEY(self):
        return self.MINIO_ROOT_USER

    @property
    def MINIO_SECRET_KEY(self):
        return self.MINIO_ROOT_PASSWORD

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env.dev",
        extra="ignore",
    )


settings = Settings()  # type: ignore
