from pathlib import Path
import pytest
import tempfile
import os
import multiprocessing
import time
import requests
import socket
import subprocess
import uvicorn


from dor.cli.client.upload_client import run_upload_fileset
from dor.cli.main import app
from dor.entrypoints.api.main import app as fastapi_app

from fastapi import FastAPI, HTTPException
from httpx import AsyncClient, ASGITransport
from typer.testing import CliRunner
from unittest.mock import patch

mock_api = FastAPI()
runner = CliRunner()
transport = ASGITransport(app=mock_api)

@mock_api.post("/api/v1/filesets")
async def mock_upload_fileset():
    return {
        "message": "Fileset uploaded successfully",
        "fileset_id": "fileset001",
        "status": "uploaded",
    }


@pytest.fixture
def fixture_path():
    return Path("tests/fixtures/test_cli_upload")

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
    api_proc = multiprocessing.Process(target=run_server)
    api_proc.start()
    assert wait_for_port(8000, "0.0.0.0"), "FastAPI did not start in time"

    yield

    api_proc.terminate()
    api_proc.join()


@pytest.mark.asyncio
async def test_run_upload_fileset():
    temp_files = []
    profiles= {}
    try:
        for i in range(2):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            temp_file.write(f"Sample content for file {i}".encode())
            temp_file.close()
            profiles[os.path.basename(temp_file.name)] = ["compress-source"]
            temp_files.append(temp_file.name)

        async with AsyncClient(transport=transport, base_url="http://test") as client:
            result = await run_upload_fileset(
                client,
                base_url="http://test",
                folder="/tmp",
                name="Test Fileset",
                project_id="Test Collection",
                profiles=profiles,
            )
            output = result
            assert "fileset_id" in output
            assert output["fileset_id"] == "fileset001"
            assert output["status"] == "uploaded"
            assert output["message"] == "Fileset uploaded successfully"
    finally:
        for temp_file in temp_files:
            os.remove(temp_file)


def test_upload_command_works_for_image(fixture_path, start_fastapi_server):

    result = runner.invoke(
        app,
        [
            "fileset",
            "upload",
            "--folder",
            fixture_path,
            "--project-id",
            "Test Collection",
            "--image",
            "compress-source"
        ],
    )
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."    

def test_upload_command_works_for_image_and_text(fixture_path, start_fastapi_server):
    result = runner.invoke(
        app,
        [
            "fileset",
            "upload",
            "--folder",
            fixture_path,
            "--project-id",
            "Test Collection",
            "--image",
            "compress-source",
            "--text",
            "label-service",
        ],
    )
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."


def test_upload_command_works_for_text(fixture_path, start_fastapi_server):
    result = runner.invoke(
        app,
        [
            "fileset",
            "upload",
            "--folder",
            fixture_path,
            "--project-id",
            "Test Collection",
            "--text",
            "label-service",
        ],
    )
    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."


def test_upload_command_works_for_no_profile(fixture_path, start_fastapi_server):
    result = runner.invoke(
        app,
        [
            "fileset",
            "upload",
            "--folder",
            fixture_path,
            "--project-id",
            "Test Collection",
        ],
    )
    assert result.exit_code == 1
    assert result.output == "No profiles provided. Use --image or --text to specify profiles.\n"
