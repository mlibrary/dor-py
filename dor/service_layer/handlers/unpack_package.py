from dor.domain.events import PackageUnpacked, PackageVerified
from dor.domain.models import VersionInfo
from dor.providers.file_provider import FileProvider
from dor.service_layer.unit_of_work import AbstractUnitOfWork
from gateway.coordinator import Coordinator


def unpack_package(
    event: PackageVerified,
    uow: AbstractUnitOfWork,
    bag_adapter_class: type,
    package_resource_provider_class: type,
    workspace_class: type,
    file_provider: FileProvider,
) -> None:
    workspace = workspace_class(event.workspace_identifier)
    bag_adapter = bag_adapter_class.load(workspace.package_directory(), file_provider)

    info = bag_adapter.dor_info
    workspace.root_identifier = info["Root-Identifier"]
    resources = package_resource_provider_class(
        workspace.object_data_directory(), file_provider
    ).get_resources()

    root_resource = [r for r in resources if str(r.id) == info["Root-Identifier"]][0]
    preservation_event = [e for e in root_resource.events if e.type == "ingest"][0]

    unpacked_event = PackageUnpacked(
        identifier=info["Root-Identifier"],
        tracking_identifier=event.tracking_identifier,
        package_identifier=event.package_identifier,
        workspace_identifier=event.workspace_identifier,
        update_flag=event.update_flag,
        resources=resources,
        version_info=VersionInfo(
            coordinator=Coordinator(
                preservation_event.agent.address, preservation_event.agent.address
            ),
            message=preservation_event.detail,
        ),
    )
    uow.add_event(unpacked_event)
