from dor.domain.events import PackageEvent
from dor.domain.models import WorkflowEvent, WorkflowEventType
from dor.service_layer.unit_of_work import AbstractUnitOfWork


def record_workflow_event(event: PackageEvent, uow: AbstractUnitOfWork):
    with uow:
        uow.event_store.add(WorkflowEvent.create(
            tracking_identifier=event.tracking_identifier,
            package_identifier=event.package_identifier,
            event_type=WorkflowEventType(event.__class__.__name__),
            message=getattr(event, "message") if hasattr(event, "message") else None
        ))
        uow.commit()
