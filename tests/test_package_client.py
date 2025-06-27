import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from dor.cli.client.package_client import (
    DepositGroup,
    PackageUploadError,
    get_package_metadata_records,
    upload_package,
    upload_packages
)


@pytest.fixture
def fixtures_path() -> Path:
    return Path("tests/fixtures/test_package_client")


@pytest.fixture
def deposit_group() -> DepositGroup:
    return DepositGroup(
        identifier="1760d69d-2e5a-4296-bfe0-d847f9f4fd4b",
        date=datetime(2025, 5, 29, 12, tzinfo=UTC)
    )


@pytest.fixture
def mocked_httpx_client() -> httpx.AsyncClient:
    async def handler(request: httpx.Request):
        data = json.loads(request.content.decode("utf-8"))
        package_identifier = data["package_metadata"]["identifier"]
        deposit_group_identifier = data["deposit_group"]["identifier"]
        data = {
            "identifier": package_identifier,
            "deposit_group_identifier": deposit_group_identifier
        }
        return httpx.Response(200, json=data)

    httpx_client = httpx.AsyncClient(
        base_url="http://localhost:8000/api/v1/",
        transport=httpx.MockTransport(handler)
    )
    return httpx_client


@pytest.fixture
def mocked_failure_httpx_client() -> httpx.AsyncClient:
    async def handler(request):
        return httpx.Response(status_code=500)

    httpx_client = httpx.AsyncClient(
        base_url="http://localhost:8000/api/v1/",
        transport=httpx.MockTransport(handler)
    )
    return httpx_client


def test_get_package_metadata_records_parses_packet_file(fixtures_path: Path, deposit_group: DepositGroup):
    packet_path = fixtures_path / "test_packet.jsonl"
    package_metadatas = list(get_package_metadata_records(packet_path))
    assert len(package_metadatas) == 2


def test_upload_package_uploads(
    fixtures_path: Path,
    deposit_group: DepositGroup,
    mocked_httpx_client: httpx.AsyncClient
):
    packet_path = fixtures_path / "test_packet.jsonl"
    package_metadatas = list(get_package_metadata_records(packet_path))
    package_metadata = package_metadatas[0]

    result = asyncio.run(upload_package(
        client=mocked_httpx_client,
        deposit_group=deposit_group,
        package_metadata=package_metadata
    ))

    assert result == {
        "identifier": "00000000-0000-0000-0000-000000000001",
        "deposit_group_identifier": "1760d69d-2e5a-4296-bfe0-d847f9f4fd4b"
    }


def test_upload_package_raises_exception_on_http_error(
    fixtures_path: Path,
    deposit_group: DepositGroup,
    mocked_failure_httpx_client: httpx.AsyncClient
):
    packet_path = fixtures_path / "test_packet.jsonl"
    package_metadatas = list(get_package_metadata_records(packet_path))
    package_metadata = package_metadatas[0]

    with pytest.raises(PackageUploadError) as excinfo:
        asyncio.run(upload_package(
            client=mocked_failure_httpx_client,
            deposit_group=deposit_group,
            package_metadata=package_metadata
        ))
    exception = excinfo.value
    assert exception.package_identifier == "00000000-0000-0000-0000-000000000001"


def test_upload_packages_uploads(
    fixtures_path: Path,
    deposit_group: DepositGroup,
    mocked_httpx_client: httpx.AsyncClient
):
    packet_path = fixtures_path / "test_packet.jsonl"

    result = asyncio.run(upload_packages(
        packet_path=packet_path,
        httpx_client=mocked_httpx_client,
        deposit_group=deposit_group
    ))

    expected_response_datas = [
        {
            "identifier": "00000000-0000-0000-0000-000000000001",
            "deposit_group_identifier": "1760d69d-2e5a-4296-bfe0-d847f9f4fd4b"
        },
        {
            "identifier": "00000000-0000-0000-0000-000000000002",
            "deposit_group_identifier": "1760d69d-2e5a-4296-bfe0-d847f9f4fd4b"
        },
    ]
    assert result.response_datas == expected_response_datas
    assert len(result.exceptions) == 0
