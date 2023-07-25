from pydantic.v1 import BaseSettings


class DatabaseSettings(BaseSettings):
    PATH: str = 'database.sqlite3'

    class Config:
        env_prefix = 'DB_'


database_settings = DatabaseSettings()
