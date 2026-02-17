from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        # DSN
        # postgresql+asyncpg://postgres:postgres@localhost:5432/sa
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_psycopg(self):
        # DSN
        # postgresql+psycopg://postgres:postgres@localhost:5432/sa
        return f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # env file
    model_config = SettingsConfigDict(
        env_file=".env.dev",  # Указываем имя вашего файла
        env_file_encoding="utf-8",
        extra="ignore",  # Игнорировать лишние переменные в файле
    )


settings = Settings()  # type: ignore
