import os
from pathlib import Path
from dotenv import load_dotenv

import sqlalchemy
from pydantic.dataclasses import dataclass


load_dotenv()

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
    pocket_base_username: str
    pocket_base_password: str
    pocket_base_url: str

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
                database=os.getenv("POSTGRES_DATABSE", "dor_local"),
                test_database=os.getenv("POSTGRES_TEST_DATABASE", "dor_test")
            ),
            pocket_base_username=os.getenv("POCKET_BASE_USERNAME", ""),
            pocket_base_password=os.getenv("POCKET_BASE_PASSWORD", ""),
            pocket_base_url=os.getenv("POCKET_BASE_URL", "")
            
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
