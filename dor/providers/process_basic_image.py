from pathlib import Path
import shutil

from dor.providers.file_system_file_provider import FilesystemFileProvider

def data_dir(identifier):
    return Path(identifier)/"data"

def target(identifier):
    return data_dir(identifier)/(identifier + ".function:source.known")


def process_basic_image(identifier: str, input_path: Path, output_path: Path) -> bool: 
    file_provider = FilesystemFileProvider()
    file_provider.create_directories(output_path/data_dir(identifier))
    for filepath in  input_path.iterdir():
        shutil.copyfile(filepath, output_path/target(identifier))
        break
    return True