from dor.settings import template_env

from dor.providers.models import PreservationEvent


class PreservationEventSerializer():

    template = template_env.get_template("premis_event.xml")

    def __init__(self, event: PreservationEvent):
        self.event = event

    def serialize(self) -> str:
        event_data = {
            "identifier": self.event.identifier,
            "type": self.event.type,
            "date_time": self.event.datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "detail": self.event.detail,
            "linking_agent": {
                "type": self.event.agent.role,
                "value": self.event.agent.address
            }
        }
        return self.template.render(event=event_data)
