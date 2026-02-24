from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    lakefilter_base_url: str = "http://lakefilter:8080"
    lakeglimpse_base_url: str = "http://lakeglimpse:5000"
    search_timeout: float = 10.0
    default_result_limit: int = 5
    log_level: str = "INFO"
    brave_api_key: str | None = None


settings = Settings()
