import typer
from dor.domain.events import PackageSubmitted
from dor.service_layer.framework import create_repo, workframe
from utils.minter import minter

app = typer.Typer(no_args_is_help=True)


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
