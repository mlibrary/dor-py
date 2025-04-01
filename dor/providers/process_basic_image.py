from pathlib import Path
import shutil

from dor.providers.file_system_file_provider import FilesystemFileProvider


def data_dir(identifier):
    return Path(identifier) / "data"


def target(identifier, basename):
    return data_dir(identifier) / (basename + ".function:source.known")


def process_basic_image(identifier: str, input_path: Path, output_path: Path) -> bool:
    file_provider = FilesystemFileProvider()
    file_provider.create_directories(output_path / data_dir(identifier))
    for filepath in input_path.iterdir():
        basename = filepath.stem
        shutil.copyfile(filepath, output_path / target(identifier, basename))
        break
    return True
