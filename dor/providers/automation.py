from dor.queues import queues
from tests.test_package_generator import deposit_group


def run_automation(event: str, **kwargs):

    match event:
        case "package.create":
            from dor.providers.packages import create_package_from_metadata
            queues["package"].enqueue(
                create_package_from_metadata,
                **kwargs
            )
        case "package.success":
            print(kwargs.get("package_identifier"))
        case _:
            raise Exception
    