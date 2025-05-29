import asyncio
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from dor.cli.client.package_client import (
    DepositGroup,
    get_package_metadatas,
    upload_package,
    upload_packages
)


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_cli_package_upload")


@pytest.fixture
def deposit_group() -> DepositGroup:
    return DepositGroup(
        identifier="1760d69d-2e5a-4296-bfe0-d847f9f4fd4b",
        date=datetime(2025, 5, 29, 12, tzinfo=UTC)
    )


@pytest.fixture
def mocked_httpx_client() -> httpx.AsyncClient:
    async def handler(request):
        data = {
            "identifier": "00000000-0000-0000-0000-000000000001",
            "deposit_group_identifier": "1760d69d-2e5a-4296-bfe0-d847f9f4fd4b"
        }
        return httpx.Response(200, json=data)

    httpx_client = httpx.AsyncClient(
        base_url="http://localhost:8000/api/v1/",
        transport=httpx.MockTransport(handler)
    )
    return httpx_client


def test_get_package_metadatas_parses_packet_file(fixtures_path: Path, deposit_group: DepositGroup):
    packet_path = fixtures_path / "test_packet.jsonl"
    package_metadatas = get_package_metadatas(packet_path)
    assert len(package_metadatas) == 1


def test_upload_package_makes_request(
    fixtures_path: Path,
    deposit_group: DepositGroup,
    mocked_httpx_client: httpx.AsyncClient
):
    packet_path = fixtures_path / "test_packet.jsonl"
    package_metadatas = get_package_metadatas(packet_path)
    package_metadata = package_metadatas[0]

    result = asyncio.run(upload_package(
        client=mocked_httpx_client,
        deposit_group=deposit_group,
        package_metadata=package_metadata
    ))
    print(result)
    assert result is not None


def test_upload_packages_uploads_one_package(
    fixtures_path: Path,
    deposit_group: DepositGroup,
    mocked_httpx_client: httpx.AsyncClient
):
    packet_path = fixtures_path / "test_packet.jsonl"
    package_metadatas = get_package_metadatas(packet_path)

    results = asyncio.run(upload_packages(
        client=mocked_httpx_client,
        deposit_group=deposit_group,
        package_metadatas=package_metadatas
    ))
    assert len(results) == 1
    assert not isinstance(results[0], Exception)
