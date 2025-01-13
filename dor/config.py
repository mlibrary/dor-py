import os

import sqlalchemy
from pydantic.dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str
    user: str
    password: str
    database: str
    test_database: str


@dataclass
class Config:
    database: DatabaseConfig

    @classmethod
    def from_env(cls):
        return cls(
            database=DatabaseConfig(
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                host=os.getenv("POSTGRES_HOST", "db"),
                database=os.getenv("POSTGRES_DATABSE", "dor_local"),
                test_database=os.getenv("POSTGRES_TEST_DATABASE", "dor_test")
            )
        )

    def get_database_engine_url(self, test=False):
        url = sqlalchemy.engine.URL.create(
            drivername="postgresql+psycopg",
            username=self.database.user,
            password=self.database.password,
            host=self.database.host,
            database=self.database.test_database if test else self.database.database
        )
        return url

config = Config.from_env()