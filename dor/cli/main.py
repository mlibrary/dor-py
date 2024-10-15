import typer
import dor.cli.samples as samples

app = typer.Typer()
app.add_typer(samples.app, name="samples")


if __name__ == "__main__":  # pragma: no cover
    app()
