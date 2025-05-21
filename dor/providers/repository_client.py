from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class FileSetSearchResult:
    file_set_identifier: str
    bin_identifier: str


class RepositoryClient(ABC):

    @abstractmethod
    def search_for_file_set(self, file_set_identifier: str) -> list[FileSetSearchResult]:
        raise NotImplementedError


class FakeRepositoryClient(RepositoryClient):

    def search_for_file_set(self, file_set_identifier: str) -> list[FileSetSearchResult]:
        return []
