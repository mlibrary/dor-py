import typer

import dor.cli.samples as samples
import dor.cli.repo as repo
from dor.cli.upload import upload_app
from dor.cli.audit import audit_app
from dor.cli.package import package_app
from dor.cli.aptrustish import aptrust_app


app = typer.Typer(no_args_is_help=True)
app.add_typer(samples.app, name="samples")
app.add_typer(repo.app, name="repo")
app.add_typer(upload_app, name="fileset")
app.add_typer(audit_app, name="audit")
app.add_typer(package_app, name="package")
app.add_typer(aptrust_app, name="aptrust")


@app.callback()
def banner():
    """
    DOR Utilities

    The various DOR command line utilities are packaged as a command suite.
    Use --help to explore the subcommands.
    """
