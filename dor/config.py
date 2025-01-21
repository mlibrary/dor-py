from dor.providers.file_provider import FileProvider
from dor.providers.file_system_file_provider import FilesystemFileProvider
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
    def from_env(cls, file_provider: FileProvider):
        return cls(
            database=DatabaseConfig(
                user=file_provider.get_environment_variable(
                    "POSTGRES_USER", "postgres"
                ),
                password=file_provider.get_environment_variable(
                    "POSTGRES_PASSWORD", "postgres"
                ),
                host=file_provider.get_environment_variable("POSTGRES_HOST", "db"),
                database=file_provider.get_environment_variable(
                    "POSTGRES_DATABSE", "dor_local"
                ),
                test_database=file_provider.get_environment_variable(
                    "POSTGRES_TEST_DATABASE", "dor_test"
                ),
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


config = Config.from_env(file_provider=FilesystemFileProvider())
