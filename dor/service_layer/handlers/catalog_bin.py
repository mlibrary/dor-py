from dor.domain.events import PackageStored, BinCataloged
from dor.service_layer.unit_of_work import AbstractUnitOfWork
from dor.domain.models import Bin

def catalog_bin(event: PackageStored, uow: AbstractUnitOfWork) -> None:
    root_resource = [resource for resource in event.resources if resource.type == 'Monograph'][0]

    bin = Bin(
        identifier=event.identifier,
        alternate_identifiers=[root_resource.alternate_identifier.id],
        common_metadata={},
        package_resources=event.resources
    )
    with uow:
        uow.catalog.add(bin)
        uow.commit()

    uow.add_event(BinCataloged(identifier=event.identifier, tracking_identifier=event.tracking_identifier))
    