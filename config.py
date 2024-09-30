from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    TOKEN: SecretStr
    DB_URL: str
    USERS: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
