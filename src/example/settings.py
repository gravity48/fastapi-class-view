from pydantic.v1 import BaseSettings


class DatabaseSettings(BaseSettings):
    PATH: str = 'test_alembic'

    class Config:
        env_prefix = 'DB_'


database_settings = DatabaseSettings()
