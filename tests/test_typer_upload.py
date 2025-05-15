import ast
import json
from dor.providers.operations import Operation
import pytest
import tempfile
import os
import multiprocessing
import time
import requests
import socket
import subprocess
import uvicorn
import re

from dor.cli.client.upload_client import run_upload_fileset
from dor.cli.main import app
from dor.entrypoints.api.main import app as fastapi_app

from fastapi import FastAPI, HTTPException
from httpx import AsyncClient
from typer.testing import CliRunner
from unittest.mock import patch

mock_api = FastAPI()
runner = CliRunner()


@mock_api.post("/api/v1/filesets")
async def mock_upload_fileset():
    return {
        "message": "Fileset uploaded successfully",
        "fileset_id": "fileset001",
        "status": "uploaded",
    }


@pytest.mark.asyncio
async def test_run_upload_fileset():
    temp_files = []
    try:
        for i in range(2):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            temp_file.write(f"Sample content for file {i}".encode())
            temp_file.close()
            temp_files.append(temp_file.name)

        async with AsyncClient(app=mock_api, base_url="http://test") as client:
            result = await run_upload_fileset(
                client,
                base_url="http://test",
                file=temp_files,  # Provide the list of files here
                folder=None,
                name="Test Fileset",
                project_id="Test Collection",
                commands="""
                {{
                    "{file_path}": {{
                        "operation": "AppendUses",
                        "args": {{
                            "target": {{
                                "function": ["function:source"],
                                "format": "format:text-plain"
                            }},
                            "uses": ["function:service"]
                        }}
                    }}
                }}
                """,
            )
            output = result[0]
            assert "fileset_id" in output
            assert output["fileset_id"] == "fileset001"
            assert output["status"] == "uploaded"
            assert output["message"] == "Fileset uploaded successfully"
    finally:
        for temp_file in temp_files:
            os.remove(temp_file)


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


def test_upload_single_file_command(start_fastapi_server):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
            temp_file.write(b"Sample content for testing.")
            test_file = temp_file.name

            f = open("/app/tmp/wtf.txt", "w")
            f.write("HEY SOMETHING")
            f.close()
            test_file = "/app/tmp/wtf.txt"

            result = runner.invoke(
                app,
                [
                    "upload",
                    "run",
                    "--file",
                    test_file,
                    "--name",
                    "TestFileset",
                    "--project-id",
                    "TestCollection",
                    "--commands",
                    """
                    {{
                        "{file_path}": {{
                            "operation": "AppendUses",
                            "args": {{
                                "target": {{
                                    "function": ["function:source"],
                                    "format": "format:text-plain"
                                }},
                                "uses": ["function:service"]
                            }}
                        }}
                    }}
                    """,
                ],
            )
            assert (
                result.exit_code == 0
            ), f"Command failed with exit code {result.exit_code}."
            assert "Fileset created successfully" in result.output
    finally:
        os.remove(test_file)


# def test_upload_command_with_multiple_files(start_fastapi_server):
#     temp_files = []
#     try:
#         for i in range(2):
#             temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
#             temp_file.write(f"Sample content for file {i}".encode())
#             temp_file.close()
#             temp_files.append(temp_file.name)

#         name = os.path.basename(temp_files[0])
#         project_id = "test_collection"
#         commands = "basic-image"

#         result = runner.invoke(
#             app,
#             [
#                 "upload",
#                 "run",
#                 "--file",
#                 temp_files[0],
#                 "--file",
#                 temp_files[1],
#                 "--name",
#                 name,
#                 "--project-id",
#                 project_id,
#                 "--commands",
#                 """
#                 {{
#                     "{file_path}": {{
#                         "operation": "AppendUses",
#                         "args": {{
#                             "target": {{
#                                 "function": ["function:source"],
#                                 "format": "format:text-plain"
#                             }},
#                             "uses": ["function:service"]
#                         }}
#                     }}
#                 }}
#                 """,
#             ],
#         )
#         print(result.output)
#         # Assert the command executed successfully
#         assert (
#             result.exit_code == 0
#         ), f"Command failed with exit code {result.exit_code}."
#         assert (
#             "Fileset created successfully" in result.output
#         ), "Expected success message in output."

#         # Parse the output and validate the response
#         parsed = extract_dict_from_output(result.stdout)

#         assert "name" in parsed, "Expected 'name' key in response."
#         assert (
#             parsed["name"] == name
#         ), f"Expected name '{name}', got '{parsed['name']}'."

#         assert "coll" in parsed, "Expected 'coll' key in response."
#         assert (
#             parsed["coll"] == project_id
#         ), f"Expected project_id '{project_id}', got '{parsed['coll']}'."

#         assert "commands" in parsed, "Expected 'commands' key in response."
#         assert (
#             parsed["commands"] == commands
#         ), f"Expected commands '{commands}', got '{parsed['commands']}'."

#         assert "files" in parsed, "Expected 'files' key in response."
#         assert (
#             len(parsed["files"]) == 2
#         ), f"Expected 2 files, got {len(parsed['files'])}."

#         # Validate file names in the response
#         uploaded_files = [os.path.basename(f) for f in temp_files]
#         for uploaded_file in uploaded_files:
#             assert (
#                 uploaded_file in parsed["files"]
#             ), f"Expected file '{uploaded_file}' in response files."
#     finally:
#         # Clean up temporary files
#         for temp_file in temp_files:
#             os.remove(temp_file)


def test_upload_command_from_folder(start_fastapi_server):
    temp_dir = tempfile.TemporaryDirectory()
    try:
        for i in range(3):
            with open(os.path.join(temp_dir.name, f"file_{i}.txt"), "w") as temp_file:
                temp_file.write(f"Sample content for file {i}")

        folder_path = temp_dir.name
        project_id = "test_collection"
        name = "test_fileset"

        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        commands = {
            file: {
                "operation": "AppendUses",
                "args": {
                    "target": {
                        "function": ["function:source"],
                        "format": "format:text-plain",
                    },
                    "uses": ["function:service"],
                },
            }
            for file in files
        }

        result = runner.invoke(
            app,
            [
                "upload",
                "run",
                "--folder",
                folder_path,
                "--name",
                name,
                "--project-id",
                project_id,
                "--commands",
                json.dumps(commands),
            ],
        )

        assert (
            result.exit_code == 0
        ), f"Command failed with exit code {result.exit_code}."
        parsed = extract_dict_from_output(result.stdout)

        assert (
            parsed["coll"] == project_id
        ), f"Expected project_id '{project_id}', got '{parsed['coll']}'."
        assert (
            parsed["commands"] == commands
        ), f"Expected commands '{commands}', got '{parsed['commands']}'."
        assert len(parsed["files"]) == len(
            files
        ), f"Expected {len(files)} files, got {len(parsed['files'])}."
    finally:
        temp_dir.cleanup()


def test_upload_command_invalid_file(start_fastapi_server):
    invalid_file_path = "non_existent_file.txt"
    name = "Test Fileset"
    project_id = "test_collection"

    # Invoke the CLI command with an invalid file path
    result = runner.invoke(
        app,
        [
            "upload",
            "run",
            "--file",
            invalid_file_path,
            "--name",
            name,
            "--project-id",
            project_id,
            "--commands",
            "{}",
        ],
    )
    # Assert that the command fails
    assert result.exit_code != 0, "Command should fail for an invalid file path."
    assert (
        f"Upload error: [Error 404] File '{invalid_file_path}' does not exist."
        in result.stdout
    ), f"Expected error message for invalid file path, got: {result.stdout}"


def extract_dict_from_output(output):
    match = re.search(r"\{.*\}", output, re.DOTALL)
    if not match:
        raise ValueError(f"Failed to extract dictionary from output: {output}")
    try:
        return ast.literal_eval(match.group(0))
    except SyntaxError as e:
        raise ValueError(
            f"Invalid dictionary syntax in output: {match.group(0)}"
        ) from e
