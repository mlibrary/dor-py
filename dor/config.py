import os
from pathlib import Path

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
    storage_path: Path
    inbox_path: Path
    workspaces_path: Path
    database: DatabaseConfig

    @classmethod
    def from_env(cls):
        return cls(
            storage_path=Path(os.getenv("STORAGE_PATH", "")),
            inbox_path=Path(os.getenv("INBOX_PATH", "")),
            workspaces_path=Path(os.getenv("WORKSPACES_PATH", "")),
            database=DatabaseConfig(
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                host=os.getenv("POSTGRES_HOST", "db"),
                database=os.getenv("POSTGRES_DATABASE", "dor_local"),
                test_database=os.getenv("POSTGRES_TEST_DATABASE", "dor_test")
            )
        )

    def _make_database_engine_url(self, database: str):
        url = sqlalchemy.engine.URL.create(
            drivername="postgresql+psycopg",
            username=self.database.user,
            password=self.database.password,
            host=self.database.host,
            database=database
        )
        return url

    def get_database_engine_url(self):
        return self._make_database_engine_url(self.database.database)

    def get_test_database_engine_url(self):
        return self._make_database_engine_url(self.database.test_database)


config = Config.from_env()
