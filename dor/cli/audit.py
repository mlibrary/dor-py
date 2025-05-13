import asyncio
import typer
import httpx

from typing import Any, Optional
from rich.console import Console
from rich.table import Table

from dor.config import config
from dor.cli.client.audit_client import AuditError, fetch_audit_status

audit_app = typer.Typer()
console = Console()


@audit_app.command(name="run")
def audit(
    project: str = typer.Option(..., help="The project name (required)"),
    isid: Optional[str] = typer.Option(
        None, help="Delivery/batch ID for a specific check (optional)"
    ),
    group_by: Optional[str] = typer.Option(
        "isid", help="Group results by 'isid', 'date', or 'status' (default: 'isid')"
    ),
    status: Optional[str] = typer.Option(
        None, help="Filter by status (completed, failed, queued, etc.)"
    ),
):
    asyncio.run(_audit(project, isid, group_by, status))


async def _audit(
    project: str,
    isid: Optional[str] = None,
    group_by: Optional[str] = "isid",
    status: Optional[str] = None,
):    
    base_url = config.api_url

    try:
        async with httpx.AsyncClient() as client:
            upload_statuses = await fetch_audit_status(
                client, base_url, project, isid, group_by, status
            )

        console.print(f"Upload status for project {project}:", style="bold cyan")
        if isinstance(upload_statuses, dict):
            for group, items in upload_statuses.items():
                console.print(f"[bold green]Group: {group}[/bold green]")
                render_table(items)
        else:
            render_table(upload_statuses)

        # return {"upload_statuses": upload_statuses}
    except AuditError as exc:
        console.print(f"Audit error: {exc}", style="bold white on red")
        raise typer.Exit(1)

    except httpx.HTTPStatusError as exc:
        handle_http_error(exc, project)

    except Exception as exc:
        # Catch any other unexpected exceptions
        console.print(
            f"An unexpected error occurred: {exc}",
            style="bold white on red",
        )
        raise typer.Exit(1)

def handle_http_error(exc, project):
    detail = exc.response.json().get("detail", "")
    if f"Project '{project}' not found" in detail:
        console.print(f"Project '{project}' was not found.", style="bold red")
        raise typer.Exit(1)
    console.print(
        f"HTTP error occurred: {exc.response.status_code} - {detail}",
        style="bold red",
    )
    raise typer.Exit(1)

def render_table(items):
    table = Table(show_header=True, header_style="bold magenta")
    if items and isinstance(items, list) and isinstance(items[0], dict):
        for key in items[0].keys():
            table.add_column(key.capitalize())
        for item in items:
            table.add_row(*[str(value) for value in item.values()])
    console.print(table)
