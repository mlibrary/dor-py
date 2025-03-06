import typer
from dor.domain.events import PackageSubmitted
from dor.service_layer import create_repo, workframe
from utils import minter

app = typer.Typer()

@app.command()
def initialize():
    create_repo()

@app.command()
def store(
    package_identifier: str = typer.Option(help="Name of the package directory"),
):
    message_bus, uow = workframe()
    event = PackageSubmitted(
        package_identifier=package_identifier,
        tracking_identifier=minter()
    )
    message_bus.handle(event, uow)
