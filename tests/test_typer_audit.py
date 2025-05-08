import pytest
from typer.testing import CliRunner
from dor.cli.main import app
from unittest.mock import patch
import httpx
import re

runner = CliRunner()

@pytest.fixture
def mock_httpx():
    with patch("dor.cli.audit.httpx") as mock:
        yield mock


def test_check_status_success(mock_httpx):

    project_id = "dor123"
    mock_httpx.get.return_value.status_code = 200
    mock_httpx.get.return_value.json.return_value = {
        "group1": [
            {
                "name": "file1.txt",
                "status": "completed",
                "project": project_id,
                "isid": "batch001",
                "date": "2025-05-01",
            },
            {
                "name": "file2.txt",
                "status": "queued",
                "project": project_id,
                "isid": "batch001",
                "date": "2025-05-02",
            },
        ],
        "group2": [
            {
                "name": "file3.txt",
                "status": "failed",
                "project": project_id,
                "isid": "batch003",
                "date": "2025-05-03",
            },
        ],
    }

    result = runner.invoke(
        app,
        [
            "audit", 
            "audit",
            "--project",
            project_id,
        ],
    )

    output = strip_ansi(result.output)

    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."
    assert f"Upload status for project '{project_id}':" in output
    assert "Group: group1" in output
    assert "file1.txt" in output
    assert "file2.txt" in output
    assert "Group: group2" in output
    assert "file3.txt" in output


def test_check_status_missing_project():

    result = runner.invoke(
        app,
        [
            "audit",
            "audit",
        ],
    )

    assert (
        result.exit_code == 2
    ), "Command should fail with exit code 2 when '--project' is missing."
    assert (
        "Missing option '--project'." in result.output
    ), f"Expected error message for missing '--project', got: {result.output}"

def test_check_status_http_error_incorrect_project():

    project_id = "invalid_project"

    result = runner.invoke(
        app,
        [
            "audit",
            "audit",
            "--project",
            project_id,
        ],
    )
    output = strip_ansi(result.output)
    assert result.exit_code == 1, "Command should fail with an HTTP error."
    assert (
        f"Project '{project_id}' was not found." in output
    ), f"Expected project not found message, got: {output}"


def strip_ansi(text):

    ansi_escape = re.compile(r"\x1b\[([0-9;]*[mGKF])")
    return ansi_escape.sub("", text)
