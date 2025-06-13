from dor.adapters import eventpublisher
from dor.domain.events import PackageIngested, PackageSubmitted
from dor.queues import queues
from dor.service_layer.framework import workframe
from utils.minter import minter


def ingest_package(package_identifier: str) -> None:
    message_bus, uow = workframe()

    tracking_identifier = minter()
    event = PackageSubmitted(
        package_identifier=package_identifier,
        tracking_identifier=tracking_identifier
    )
    # TODO: Uncomment once create_package_from_metadata is working
    # message_bus.handle(event, uow)

    # Move this to the PackageSubmitted handler -- stubbed to show flow
    print(f"WOULD INGEST this package: {package_identifier}")
    eventpublisher.publish(PackageIngested(
        package_identifier=package_identifier,
        tracking_identifier=tracking_identifier
    ))
