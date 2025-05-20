import typer
import dor.cli.samples as samples
import dor.cli.repo as repo

app = typer.Typer(no_args_is_help=True)
app.add_typer(samples.app, name="samples")
app.add_typer(repo.app, name="repo")


@app.callback()
def banner():
    """
    DOR Utilities

    The various DOR command line utilities are packaged as a command suite.
    Use --help to explore the subcommands.
    """
