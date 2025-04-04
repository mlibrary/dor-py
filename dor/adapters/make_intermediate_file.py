import subprocess
from pathlib import Path


class IntermediateFileError(Exception):
    pass


def make_intermediate_file(input_path: Path, output_path: Path):
    try:
        subprocess.run(
            ["vips", "tiffsave", f"{input_path}[autorotate]", output_path, "--compression", "none"],
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        raise IntermediateFileError from e
