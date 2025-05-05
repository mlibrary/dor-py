import shutil
import subprocess
from pathlib import Path


class BitonalFileError(Exception):
    pass


def make_fake_bitonal_file(input_path: Path, output_path: Path):
    shutil.copyfile(input_path, output_path)


def make_bitonal_file(input_path: Path, output_path: Path):
    """
    Converts an image to a bitonal (1-bit) TIFF with CCITT Group 4 compression.

    Args:
        input_path: Path to the source image file
        output_path: Path where the bitonal TIFF will be saved

    Raises:
        BitonalFileError: If any of the conversion steps fail
    """
    try:
        # Create temporary filenames with the same directory as the output file
        temp_dir = output_path.parent
        temp_gray = temp_dir / "temp_gray.tiff"
        temp_threshold = temp_dir / "temp_threshold.tiff"
        temp_binary = temp_dir / "temp_binary.tiff"

        # Convert to grayscale
        subprocess.run(
            ["vips", "extract_band", str(input_path), str(temp_gray), "0"],
            capture_output=True,
            check=True
        )

        # Apply threshold
        subprocess.run(
            ["vips", "relational_const", str(temp_gray), str(temp_threshold), "less", "200"],
            capture_output=True,
            check=True
        )

        # Convert to binary format
        subprocess.run(
            ["vips", "cast", str(temp_threshold), str(temp_binary), "uchar"],
            capture_output=True,
            check=True
        )

        # Save as bitonal TIFF with CCITT Group 4 compression
        subprocess.run(
            ["vips", "copy", str(temp_binary), f"{str(output_path)}[compression=ccittfax4,squash=1]"],
            capture_output=True,
            check=True
        )

        # Clean up temporary files
        for temp_file in [temp_gray, temp_threshold, temp_binary]:
            if temp_file.exists():
                temp_file.unlink()

    except subprocess.CalledProcessError as e:
        # Clean up any temporary files that might have been created
        for temp_file in [temp_dir / "temp_gray.tiff", temp_dir / "temp_threshold.tiff", temp_dir / "temp_binary.tiff"]:
            if temp_file.exists():
                temp_file.unlink()

        stderr_output = e.stderr.decode() if e.stderr else "Unknown error"
        raise BitonalFileError(f"Error creating bitonal file: {stderr_output}") from e
