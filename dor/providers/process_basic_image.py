from pathlib import Path
import shutil

from dor.providers.file_system_file_provider import FilesystemFileProvider


def data_dir(identifier):
    return Path(identifier) / "data"


def target(identifier, basename):
    return data_dir(identifier) / (basename + ".function:source.known")


def get_source_file_path(input_path: Path) -> Path:
    for file_path in input_path.iterdir():
        return file_path
    raise Exception()


def process_basic_image(identifier: str, input_path: Path, output_path: Path) -> bool:
    file_provider = FilesystemFileProvider()
    file_provider.create_directories(output_path / data_dir(identifier))

    source_file_path = get_source_file_path(input_path)
    basename = source_file_path.stem
    shutil.copyfile(source_file_path, output_path / target(identifier, basename))
    return True
