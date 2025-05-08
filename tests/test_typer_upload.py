import ast
from typer.testing import CliRunner
from dor.cli.main import app
import os
import re
import tempfile

runner = CliRunner()


def test_upload_single_file_command():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"Sample content for testing.")
        file_path = temp_file.name

    try:
        name = os.path.basename(file_path)
        collection = "test_collection"
        profile = "basic-image"

        result = runner.invoke(
            app,
            [
                "upload",
                "upload",
                "--file",
                file_path,
                "--name",
                name,
                "--collection",
                collection,
                "--profile",
                profile,
            ],
        )

        assert (
            result.exit_code == 0
        ), f"Command failed with exit code {result.exit_code}."

        parsed = ast.literal_eval(extract_dict_from_output(result.stdout))
        assert (
            parsed["name"] == name
        ), f"Expected name '{name}', got '{parsed['name']}'."
        assert (
            parsed["coll"] == collection
        ), f"Expected collection '{collection}', got '{parsed['coll']}'."
        assert (
            parsed["profile"] == profile
        ), f"Expected profile '{profile}', got '{parsed['profile']}'."
    finally:
        os.remove(file_path)


def test_upload_command_with_multiple_files():
    temp_files = []
    try:
        # Create multiple temporary files
        for i in range(2):
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
            temp_file.write(f"Sample content for file {i}".encode())
            temp_file.close()
            temp_files.append(temp_file.name)

        name = os.path.basename(temp_files[0])
        collection = "test_collection"
        profile = "basic-image"

        result = runner.invoke(
            app,
            [
                "upload",
                "upload",
                "--file",
                temp_files[0],
                "--file",
                temp_files[1],
                "--name",
                name,
                "--collection",
                collection,
                "--profile",
                profile,
            ],
        )

        assert (
            result.exit_code == 0
        ), f"Command failed with exit code {result.exit_code}."
        parsed = ast.literal_eval(extract_dict_from_output(result.stdout))

        assert (
            parsed["name"] == name
        ), f"Expected name '{name}', got '{parsed['name']}'."
        assert (
            parsed["coll"] == collection
        ), f"Expected collection '{collection}', got '{parsed['coll']}'."
        assert (
            parsed["profile"] == profile
        ), f"Expected profile '{profile}', got '{parsed['profile']}'."
        assert (
            len(parsed["files"]) == 2
        ), f"Expected 2 files, got {len(parsed['files'])}."
    finally:
        for temp_file in temp_files:
            os.remove(temp_file)


def test_upload_command_from_folder():
    temp_dir = tempfile.TemporaryDirectory()
    try:
        # Create multiple files in the temporary directory
        for i in range(3):
            with open(os.path.join(temp_dir.name, f"file_{i}.txt"), "w") as temp_file:
                temp_file.write(f"Sample content for file {i}")

        folder_path = temp_dir.name
        collection = "test_collection"
        profile = "basic-image"
        name = "test_fileset"

        # Get all files in the folder
        files = [
            os.path.join(folder_path, f)
            for f in os.listdir(folder_path)
            if os.path.isfile(os.path.join(folder_path, f))
        ]

        result = runner.invoke(
            app,
            [
                "upload",
                "upload",
                "--folder",
                folder_path,
                "--name",
                name,
                "--collection",
                collection,
                "--profile",
                profile,
            ],
        )

        assert (
            result.exit_code == 0
        ), f"Command failed with exit code {result.exit_code}."
        parsed = ast.literal_eval(extract_dict_from_output(result.stdout))

        assert (
            parsed["coll"] == collection
        ), f"Expected collection '{collection}', got '{parsed['coll']}'."
        assert (
            parsed["profile"] == profile
        ), f"Expected profile '{profile}', got '{parsed['profile']}'."
        assert len(parsed["files"]) == len(
            files
        ), f"Expected {len(files)} files, got {len(parsed['files'])}."
    finally:
        temp_dir.cleanup()


def test_upload_command_invalid_file():
    invalid_file_path = "non_existent_file.txt"
    name = "non_existent_file.txt"
    collection = "test_collection"
    profile = "basic-image"

    result = runner.invoke(
        app,
        [
            "upload",
            "upload",
            "--file",
            invalid_file_path,
            "--name",
            name,
            "--collection",
            collection,
            "--profile",
            profile,
        ],
    )

    assert result.exit_code != 0, "Command should fail for invalid file path."
    assert (
        "Error: File" in result.stdout
    ), f"Expected error message for invalid file path, got: {result.stdout}"


def extract_dict_from_output(output):
    match = re.search(r"\{.*\}", output, re.DOTALL)
    if not match:
        raise ValueError(f"Failed to extract dictionary from output: {output}")
    return match.group(0)

