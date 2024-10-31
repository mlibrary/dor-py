from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from behave import given

@dataclass
class AssetFile:
    id: str
    path: Path

@dataclass
class Asset:
    id: str
    description: str
    files: list[AssetFile]

@dataclass
class StructMap:
    id: str
    path: Path
    asset_order: list[str]

@dataclass
class PreservedDigitalObject:
    id: str
    struct_map: StructMap
    assets: list[Asset]

    def contains_asset_with_id(self, id: str) -> bool:
        for asset in self.assets:
            if asset.id == id:
                return True
        return False

class PreservationRepositoryBase(metaclass=ABCMeta):

    @abstractmethod
    def find(self, id: str) -> PreservedDigitalObject:
        pass

    @abstractmethod
    def add(self, pdo: PreservedDigitalObject) -> None:
        pass

class FakePreservationRepository(PreservationRepositoryBase):
    store: dict[str, PreservedDigitalObject]

    def __init__(self):
        self.store = dict()

    def find(self, id: str) -> PreservedDigitalObject:
        result = self.store.get(id, None)
        if not result:
            raise Exception()
        return result

    def add(self, pdo: PreservedDigitalObject) -> None:
        self.store[pdo.id] = pdo

@given(u'an incomplete book in preservation')
def an_incomplete_book(context):
    pdo = PreservedDigitalObject(
        id="moby-dick",
        assets=[
            Asset(
                id="front-cover",
                description="Front Cover",
                files=[AssetFile(id="0001", path=Path("moby-dick/0001/0001.tiff"))]
            ),
            Asset(
                id="back-cover",
                description="Back Cover",
                files=[AssetFile(id="0425", path=Path("moby-dick/0425/0425.tiff"))]
            )
        ],
        struct_map=StructMap(
            id="struct-map",
            path=Path("moby-dick/struct-map.xml"),
            asset_order=["front-cover", "back-cover"]
        )
    )
    repo = FakePreservationRepository()
    repo.add(pdo)
    context.repo = repo

@when(u'the Collection Manager submits a package with a single page and updated metadata')
def step_impl(context):
    raise NotImplementedError(u'STEP: When the Collection Manager submits a package with a single page and updated metadata')

@then(u'the page and metadata are staged for preview')
def new_page_is_staged(context):
    repo: PreservationRepositoryBase = context.repo
    moby_dick = repo.find(id="moby-dick")

    assert moby_dick.contains_asset_with_id("title-page")
    assert moby_dick.struct_map.asset_order == ["front-cover", "title-page", "back-cover"]
