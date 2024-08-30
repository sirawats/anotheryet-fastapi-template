from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = Field(validate_default=True)
    SECRET_KEY: str = Field(validate_default=True)

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings() # type: ignore
