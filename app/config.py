from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SERVICE_EXTERNAL_PORT: int

    REDIS_USER: str
    REDIS_PASSWORD: str
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_EVENTS_STREAM: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def redis_dsn(self) -> str:
        user = self.REDIS_USER
        password = self.REDIS_PASSWORD
        host = self.REDIS_HOST
        port = self.REDIS_PORT
        return f"redis://{user}:{password}@{host}:{port}/0"

settings = Settings()
