from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    YOOKASSA_SHOP_ID: str
    YOOKASSA_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        extra="ignore",
    )


settings = Settings()  # type: ignore
