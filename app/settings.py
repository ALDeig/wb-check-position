import logging.config
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TELEGRAM_TOKEN: str
    ADMINS: list[int]
    LOG_LEVEL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_DB: str

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:5432/{self.POSTGRES_DB}"
        )


settings = Settings()  # type: ignore


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default_formatter": {
            "format": "[%(asctime)s] [%(levelname)7s] [%(name)s] > %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "stream_handler": {
            "class": "logging.StreamHandler",
            "formater": "default_formatter",
        }
    },
    "loggers": {
        "root": {
            "handlers": ["stream_handler"],
            "level": settings.LOG_LEVEL,
            "propagate": True,
        }
    },
}


logging.config.dictConfig(LOGGING_CONFIG)
