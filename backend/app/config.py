from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Quant Signal Engine"
    environment: str = "dev"
    ws_interval_seconds: float = 3.0
    default_symbol: str = "BTCUSDT"
    default_interval: str = "1m"
    prediction_threshold: float = 0.90

    binance_base_url: str = "https://api.binance.com"
    alphavantage_api_key: str | None = None
    news_api_key: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
