import pytest
import multiprocessing
import time
import socket
import subprocess
from fastapi import FastAPI
from httpx import AsyncClient
from dor.cli.client.audit_client import fetch_audit_status
from typer.testing import CliRunner
from dor.cli.main import app
from dor.entrypoints.api.main import app as fastapi_app
import uvicorn
import re

mock_api = FastAPI()
runner = CliRunner()

@mock_api.get("/api/v1/filesets/status")
async def get_status(
    project: str, isid: str = None, group_by: str = "isid", status: str = None
):
    return {"group1": [{"isid": "dor123", "status": status or "ok"}]}


@pytest.mark.asyncio
async def test_fetch_audit_status():
    async with AsyncClient(
        app=mock_api, base_url="http://test") as client:
        result = await fetch_audit_status(client, "http://test", project="dor123")
        assert "group1" in result
        assert isinstance(result["group1"], list)


def run_server():
    config = uvicorn.Config(fastapi_app, host="0.0.0.0", port=8000, log_level="error")
    server = uvicorn.Server(config)
    server.run()


def wait_for_port(port, host="0.0.0.0", timeout=5.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=0.5):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.1)
    return False


@pytest.fixture(scope="module")
def start_fastapi_server():
    proc = multiprocessing.Process(target=run_server)
    proc.start()
    assert wait_for_port(8000), "Server did not start in time"
    yield
    proc.terminate()
    proc.join()


def test_audit_success(start_fastapi_server):
    result = runner.invoke(app, ["audit", "run", "--project", "dor123"])

    output = strip_ansi(result.output)

    assert result.exit_code == 0
    assert "Upload status for project dor123:" in output
    assert "Group: batch001" in output
    assert "file1.txt" in output
    assert "file2.txt" in output
    assert "Group: batch005" in output
    assert "file3.txt" in output


def test_audit_http_error_invalid_project(start_fastapi_server):
    project_id = "invalid_project"
    result = runner.invoke(
        app,
        [
            "audit",
            "run",
            "--project",
            project_id,
        ],
    )
    output = strip_ansi(result.output)

    # Assertions
    assert result.exit_code == 1, "Command should fail with an HTTP error."
    assert (
        f"Project '{project_id}' was not found." in output
    ), f"Expected project not found message, got: {output}"


def test_audit_missing_project_argument(start_fastapi_server):
    result = runner.invoke(
        app,
        [
            "audit",
            "run"
        ],
    )
    output = strip_ansi(result.output)
    assert (
        result.exit_code == 2
    ), "Command should fail with exit code 2 when '--project' is missing."
    assert "Missing option '--project'" in output



def strip_ansi(text):
    ansi_escape = re.compile(r"\x1b\[([0-9;]*[mGKF])")
    return ansi_escape.sub("", text)
