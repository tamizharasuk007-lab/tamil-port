from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Quant Signal Engine"
    environment: str = "dev"
    news_api_key: str | None = None
    finnhub_api_key: str | None = None
    polling_interval_seconds: int = 20
    signal_probability_threshold: float = 0.9

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
