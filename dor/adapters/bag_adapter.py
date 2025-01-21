from pathlib import Path

import bagit
from dor.providers.file_provider import FileProvider 


class DorInfoMissingError(Exception):
    pass


class ValidationError(Exception):

    def __init__(self, message: str):
        super().__init__(message)

        self.message = message


class FakeBagAdapter():

    def __init__(self, identifier: str) -> None:
        self.identifier = identifier

    def validate(self) -> None:
        return
    
    @property
    def dor_info(self) -> dict:
        return {
            'Root-Identifier': "00000000-0000-0000-0000-000000000001"
        }


class BagAdapter:
    
    dor_info_file_name = "dor-info.txt"

    def __init__(self, path: Path, file_provider: FileProvider) -> None:
        self.bag = bagit.Bag(str(path))
        self.file_provider = file_provider

    def validate(self) -> None:
        try:
            self.bag.validate()
        except bagit.BagValidationError as e:
            raise ValidationError(f"Validation failed with the following message: \"{str(e)}\"")

        tag_files = [file for file in self.bag.tagfile_entries()]
        dor_info_in_tagmanifest = self.dor_info_file_name in tag_files
        if not dor_info_in_tagmanifest:
            raise ValidationError("dor-info.txt must be listed in the tagmanifest file.")
        return

    @property
    def dor_info(self) -> dict[str, str]:
        path = Path(self.bag.path)
        try:
            data = bagit._load_tag_file(self.file_provider.get_combined_path(path, self.dor_info_file_name))
        except FileNotFoundError as e:
            raise DorInfoMissingError from e
        return data
