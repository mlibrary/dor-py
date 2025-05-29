import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Generator

from fastapi.testclient import TestClient
import pytest

from dor.entrypoints.api.dependencies import get_inbox_path, get_pending_path
from dor.entrypoints.api.main import app


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_packages_api")


@pytest.fixture
def package_test_client(fixtures_path) -> Generator[TestClient, None, None]:
    def get_inbox_path_override():
        return Path("tests/output/test_packages_api/test_inbox")

    def get_pending_path_override():
        return fixtures_path / "test_pending"

    app.dependency_overrides[get_inbox_path] = get_inbox_path_override
    app.dependency_overrides[get_pending_path] = get_pending_path_override
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


def test_packages_api_returns_200_and_summary(package_test_client: TestClient, fixtures_path: Path):
    package_metadata_path = fixtures_path / "sample_package_metadata.json"
    package_metadata = json.loads(package_metadata_path.read_text())
    body = {
        "deposit_group": {
            "identifier": "1bfbeda4-ca62-4922-b104-73931ade1d21",
            "date": datetime(2025, 5, 23, 12, tzinfo=UTC).isoformat()
        },
        "package_metadata": package_metadata
    }
    response = package_test_client.post("api/v1/packages", json=body)
    assert response.status_code == 200
