import subprocess
from pathlib import Path


def make_intermediate_file(input_path: Path, output_path: Path) -> Path:
    try:
        subprocess.run(
            ["vips", "tiffsave", f"{input_path}[autorotate]", output_path, "--compression", "none" ], 
            capture_output=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print("!", e.stderr.decode("utf-8"))
        raise Exception

    return input_path
