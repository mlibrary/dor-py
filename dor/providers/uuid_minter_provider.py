import uuid
from dor.providers.minter_provider import MinterProvider


class UuidMinterProvider(MinterProvider):

    def mint(self) -> str:
        return str(uuid.uuid4())
