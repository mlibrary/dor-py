import typer
import dor.cli.samples as samples
import dor.cli.repo as repo
from dor.cli.upload import upload_app
from dor.cli.audit import audit_app

app = typer.Typer()
app.add_typer(samples.app, name="samples")
app.add_typer(repo.app, name="repo")
app.add_typer(upload_app, name="fileset")
app.add_typer(audit_app, name="audit")


if __name__ == "__main__":  # pragma: no cover
    app()
