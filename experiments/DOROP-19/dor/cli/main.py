import typer
import dor.cli.mockyrie as mockyrie

app = typer.Typer()
app.add_typer(mockyrie.app, name="mockyrie")


if __name__ == "__main__":  # pragma: no cover
    app()
