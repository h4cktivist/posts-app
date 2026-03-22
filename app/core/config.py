from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    cache_ttl: int = 60

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def database_url_async(self) -> str:
        u = self.database_url
        if u.startswith("postgresql://"):
            return u.replace("postgresql://", "postgresql+asyncpg://", 1)
        if u.startswith("postgres://"):
            return "postgresql+asyncpg://" + u[len("postgres://") :]
        return u


settings = Settings()
