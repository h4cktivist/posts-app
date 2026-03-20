from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    cache_ttl: int = 60

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
