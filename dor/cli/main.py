import typer
import dor.cli.samples as samples
import dor.cli.repo as repo

app = typer.Typer()
app.add_typer(samples.app, name="samples")
app.add_typer(repo.app, name="repo")


if __name__ == "__main__":  # pragma: no cover
    app()
