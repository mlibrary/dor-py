from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FileSetSearchResult:
    file_set_identifier: str
    bin_identifier: str


class OPClient(ABC):

    @abstractmethod
    def search_for_file_set(self, file_set_identifier: str) -> FileSetSearchResult | None:
        raise NotImplementedError


class FakeOPClient(OPClient):

    def search_for_file_set(self, file_set_identifier: str) -> FileSetSearchResult | None:
        return None
