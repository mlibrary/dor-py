from pathlib import Path
import shutil

from dor.providers.file_system_file_provider import FilesystemFileProvider


def process_basic_image(identifier: str, input_path: Path, output_path: Path) -> bool: 
    file_provider = FilesystemFileProvider()
    file_provider.create_directories(output_path/identifier/"data")
    for filepath in  input_path.iterdir():
        shutil.copyfile(filepath, output_path/identifier/"data"/(identifier + ".function:source.known"))
        break
    return True