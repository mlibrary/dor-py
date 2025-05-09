import typer
import dor.cli.samples as samples
import dor.cli.repo as repo
import dor.cli.upload as upload
import dor.cli.audit as audit

app = typer.Typer()
app.add_typer(samples.app, name="samples")
app.add_typer(repo.app, name="repo")
app.add_typer(upload.app, name="upload")
app.add_typer(audit.app, name="audit")


if __name__ == "__main__":  # pragma: no cover
    app()
