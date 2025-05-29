from pathlib import Path

import pytest
from typer.testing import CliRunner

from dor.cli.main import app as cli_app


runner = CliRunner()


@pytest.fixture
def fixtures_path():
    return Path("tests/fixtures/test_cli_package_upload")


def test_package_upload_command_runs(fixtures_path):
    packet_path = fixtures_path / "test_packet.jsonl"

    result = runner.invoke(
        cli_app,
        [
            "package",
            "upload",
            str(packet_path)
        ],
    )
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."
    print(result.stdout)


def test_package_upload_fails_with_fake_path():
    result = runner.invoke(
        cli_app,
        [
            "package",
            "upload",
            "some/fake/path"
        ],
    )
    assert result.exit_code == 1
