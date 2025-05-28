from dor.queues import queues


def run_automation(event: str, **kwargs):
    match event:
        case "package.create":
            from dor.providers.packages import create_package_from_metadata
            queues["package"].enqueue(
                create_package_from_metadata,
                deposit_group=kwargs["deposit_group"],
                package_metadata=kwargs["package_metadata"],
                inbox_path=kwargs["inbox_path"],
                pending_path=kwargs["pending_path"]
            )
        case "package.success":
            from dor.providers.ingest import ingest_package
            queues["ingest"].enqueue(
                ingest_package,
                package_identifier=kwargs["package_identifier"]
            )
        case "ingest.success":
            print(kwargs)
        case _:
            raise Exception
