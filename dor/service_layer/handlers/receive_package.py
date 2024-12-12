from dor.domain.events import PackageSubmitted, PackageReceived
from dor.service_layer.unit_of_work import UnitOfWork
from dor.domain.models import FakeWorkspace

class Translocator:

    def create_workspace_for_package(self, package_identifier: str) -> FakeWorkspace:
        return FakeWorkspace("workspace_identifier")

def receive_package(event: PackageSubmitted, uow: UnitOfWork, translocator: Translocator) -> None:
    workspace = translocator.create_workspace_for_package(event.package_identifier)

    received_event = PackageReceived(
        package_identifier=event.package_identifier,
        tracking_identifier='aintthatpeculiar',
        workspace_identifier = workspace.identifier
    )
    
    uow.add_event(received_event) 
