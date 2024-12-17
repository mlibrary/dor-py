import os
from pathlib import Path

import bagit 

class DorInfoMissingError(Exception):
    pass

class BagReader:
    
    dor_info_file_name = "dor-info.txt"

    def __init__(self, path: Path) -> None:
        self.bag = bagit.Bag(str(path))

    def is_valid(self):
        is_valid = True

        print("HELLO")

        try:
            self.bag.validate()

        except bagit.BagValidationError as e:
            print("ERROR")
            is_valid = False
            print(e)
            print(e.details)
            for d in e.details:
                print(d)
            
        # return True
        # is_valid = self.bag.is_valid()

        # print(f"is_valid: {is_valid}")

        tag_files = [file for file in self.bag.tagfile_entries()]
        dor_info_in_tagmanifest = self.dor_info_file_name in tag_files

        return is_valid and dor_info_in_tagmanifest
    
    @property
    def dor_info(self) -> dict[str, str]:
        path = self.bag.path
        try:
            data = bagit._load_tag_file(os.path.join(path, self.dor_info_file_name))
        except FileNotFoundError as e:
            raise DorInfoMissingError from e
        return data
