from dor.domain.events import PackageStored, BinCataloged
from dor.service_layer.unit_of_work import AbstractUnitOfWork
from dor.domain.models import Bin

def catalog_bin(event: PackageStored, uow: AbstractUnitOfWork) -> None:
    root_resource = [resource for resource in event.resources if resource.type == 'Monograph'][0]

    # Need to ask gatway for path to file
    # Gatway has get object file then search for logical path then get the literal path
    # Then we can add the literal path to the resource
    # root_resource.path = gatway.get_path(root_resource.identifier)
    # Going to have to parse the file name from the path and deserialize 

    # I want common metadata
    # We should already have it
    # Goes back to the root resource problem
    # We can refactor next MVP, still working with a baby sample.
    # There is a lot of work to do here

    # Roger is really good at this stuff


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
    