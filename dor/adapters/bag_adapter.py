from pathlib import Path
from typing import Self

import bagit

from dor.providers.file_provider import FileProvider 


class DorInfoMissingError(Exception):
    pass


class ValidationError(Exception):

    def __init__(self, message: str):
        super().__init__(message)

        self.message = message


class BagAdapter:
    
    dor_info_file_name = "dor-info.txt"

    @classmethod
    def load(cls, path: Path, file_provider: FileProvider) -> Self:
        bagit_bag = bagit.Bag(str(path))
        return cls(bagit_bag, file_provider)

    @classmethod
    def make(cls, payload_path: Path, file_provider: FileProvider) -> Self:
        bagit_bag = bagit.make_bag(str(payload_path))
        return cls(bagit_bag, file_provider)

    def __init__(self, bag, file_provider: FileProvider) -> None:
        self.bag = bag
        self.file_provider = file_provider

    def add_dor_info(self, dor_info: dict[str, str]) -> None:
        bagit._make_tag_file(Path(self.bag.path) / self.dor_info_file_name, dor_info)
        self.bag.save()

    @property
    def dor_info(self) -> dict[str, str]:
        path = Path(self.bag.path)
        try:
            data = bagit._load_tag_file(self.file_provider.get_combined_path(path, self.dor_info_file_name))
        except FileNotFoundError as e:
            raise DorInfoMissingError from e
        return data

    @property
    def has_dor_info(self) -> bool:
        try:
            self.dor_info
            return True
        except DorInfoMissingError:
            return False

    def validate(self) -> None:
        try:
            self.bag.validate()
        except bagit.BagValidationError as e:
            raise ValidationError(f"Validation failed with the following message: \"{str(e)}\"")

        if self.has_dor_info:
            tag_files = [file for file in self.bag.tagfile_entries()]
            dor_info_in_tagmanifest = self.dor_info_file_name in tag_files
            if not dor_info_in_tagmanifest:
                raise ValidationError("dor-info.txt must be listed in the tagmanifest file.")
        return

