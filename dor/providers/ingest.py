# from dor.domain.events import PackageSubmitted
from dor.providers.automation import run_automation
from dor.queues import queues
from dor.service_layer.framework import workframe
from utils.minter import minter


def ingest_package(package_identifier: str) -> None:
    message_bus, uow = workframe()

    tracking_identifier = minter()
    # event = PackageSubmitted(
    #     package_identifier=package_identifier,
    #     tracking_identifier=tracking_identifier
    # )
    # message_bus.handle(event, uow)

    queues["automation"].enqueue(
        run_automation,
        "ingest.success",
        package_identifier=package_identifier,
        tracking_identifier=tracking_identifier
    )
