import pytest

from pathlib import Path

from dor.domain.models import PathData


@pytest.fixture
def path_data() -> PathData:
    scratch = Path("./features/scratch")

    return PathData(
        scratch=scratch,
        inbox=Path("./features/fixtures/inbox"),
        workspaces=scratch / "workspaces",
        storage=scratch / "storage"
    )