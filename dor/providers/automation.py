from typing import Tuple

from dor.queues import queues


def run_automation(event: str, *args):

    match event:
        case "package.create":
            from dor.providers.packages import create_package_from_metadata
            queues["package"].enqueue(
                create_package_from_metadata,
                *args
            )
        case "package.success":
            print(*args)
        case _:
            raise Exception
    