from pathlib import Path
import shutil
import subprocess

class ServiceImageProcessingError(Exception):
    pass

def generate_fake_service_variant(source_file_path: Path, service_file_path: Path):
    shutil.copyfile(source_file_path, service_file_path)

# grk_compress can take as input compressed TIFF and JPEG
# but NOT when the JPEG is named ".tif"

# grok 10.x in debian bookworm has these weird quasi-long options (-EPH)
# grok 14.x (current, not in debian) has options like --eph

def generate_service_variant(input_path: Path, output_path: Path) -> None:
    try:
        # -V copies EXIF metadata, despite the docs
        subprocess.run(
            [
                "grk_compress",
                "-i",
                input_path,
                "-o",
                output_path,
                "-p",
                "RLCP",
                "-EPH",
                "-SOP",
                "-irreversible",
                "-V",
            ],
            capture_output=False,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise ServiceImageProcessingError from e
