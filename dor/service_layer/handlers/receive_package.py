from typing import Any

from dor.domain.events import PackageSubmitted, PackageReceived
from dor.service_layer.unit_of_work import UnitOfWork

def receive_package(event: PackageSubmitted, uow: UnitOfWork, translocator: Any) -> None:
    workspace = translocator.create_workspace_for_package(event.package_identifier)

    received_event = PackageReceived(
        package_identifier=event.package_identifier,
        tracking_identifier='aintthatpeculiar',
        workspace_identifier = workspace.identifier
    )
    
    uow.add_event(received_event) 
