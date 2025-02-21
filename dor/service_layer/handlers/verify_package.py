from dor.adapters.bag_adapter import ValidationError
from dor.domain.events import PackageNotVerified, PackageReceived, PackageVerified
from dor.providers.file_provider import FileProvider
from dor.service_layer.unit_of_work import AbstractUnitOfWork

def verify_package(
    event: PackageReceived, uow: AbstractUnitOfWork, bag_adapter_class: type, workspace_class: type, file_provider: FileProvider
) -> None:
    workspace = workspace_class(event.workspace_identifier)

    bag_adapter = bag_adapter_class.load(workspace.package_directory(), file_provider)

    try:
        bag_adapter.validate()
        uow.add_event(PackageVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            workspace_identifier=workspace.identifier,
            update_flag=event.update_flag,
        ))
    except ValidationError as e:
        uow.add_event(PackageNotVerified(
            package_identifier=event.package_identifier,
            tracking_identifier=event.tracking_identifier,
            message=e.message,
            update_flag=event.update_flag,
        ))
