import os
from pathlib import Path

import bagit 


class BagReader:
    
    def __init__(self, path: Path) -> None:
        self.bag = bagit.Bag(str(path))

    def is_valid(self):
        return self.bag.is_valid()
    
    @property
    def dor_info(self) -> dict[str, str]:
        path = self.bag.path
        data = bagit._load_tag_file(os.path.join(path, "dor-info.txt"))
        return data 
