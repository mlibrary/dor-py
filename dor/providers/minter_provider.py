from abc import ABC, abstractmethod

class MinterProvider(ABC):
    @abstractmethod
    def mint(self) -> str:
        pass
