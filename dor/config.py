import os
from dataclasses import dataclass
from pathlib import Path

import sqlalchemy


@dataclass
class DatabaseConfig:
    host: str
    user: str
    password: str
    database: str


@dataclass
class PocketbaseConfig:
    pb_username: str
    pb_password: str
    pb_url: str


@dataclass
class Config:
    storage_path: Path
    inbox_path: Path
    workspaces_path: Path
    database: DatabaseConfig
    pocketbase: PocketbaseConfig


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
                database=os.getenv("POSTGRES_DATABASE", "dor_local")
            ),
            pocketbase=PocketbaseConfig( 
                pb_username=os.getenv("POCKET_BASE_USERNAME", "test@umich.edu"),
                pb_password=os.getenv("POCKET_BASE_PASSWORD", "testumich"),
                pb_url=os.getenv("POCKET_BASE_URL", "http://pocketbase:8080")
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


config = Config.from_env()
