import ast
from typer.testing import CliRunner
from dor.cli.main import app
import os
import re 
runner = CliRunner()


def test_upload_single_file_command():

    file_path = "tests/test_uploads/test_file_markup.txt"
    name = "test_file_markup.txt"
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

    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."

    parsed = ast.literal_eval(extract_dict_from_output(result.stdout))
    assert parsed["name"] == name, f"Expected name '{name}', got '{parsed['name']}'."
    assert (
        parsed["coll"] == collection
    ), f"Expected collection '{collection}', got '{parsed['coll']}'."
    assert (
        parsed["profile"] == profile
    ), f"Expected profile '{profile}', got '{parsed['profile']}'."


def test_upload_command_with_multiple_files():

    file_path1 = "tests/test_uploads/test_file_markup.txt"
    file_path2 = "tests/test_uploads/test_file_2.txt"
    name = "test_file_markup.txt"
    collection = "test_collection"
    profile = "basic-image"

    result = runner.invoke(
        app,
        [
            "upload",
            "upload",
            "--file",
            file_path1,
            "--file",
            file_path2,
            "--name",
            name,
            "--collection",
            collection,
            "--profile",
            profile,
        ],
    )

    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."
    parsed = ast.literal_eval(extract_dict_from_output(result.stdout))

    assert parsed["name"] == name, f"Expected name '{name}', got '{parsed['name']}'."
    assert (
        parsed["coll"] == collection
    ), f"Expected collection '{collection}', got '{parsed['coll']}'."
    assert (
        parsed["profile"] == profile
    ), f"Expected profile '{profile}', got '{parsed['profile']}'."
    assert len(parsed["files"]) == 2, f"Expected 2 files, got {len(parsed['files'])}."


def test_upload_command_from_folder():

    folder_path = "tests/test_uploads/"
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

    assert result.exit_code == 0, f"Command failed with exit code {result.exit_code}."
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


def test_upload_command_invalid_file():

    invalid_file_path = "tests/test_uploads/non_existent_file.txt"
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
