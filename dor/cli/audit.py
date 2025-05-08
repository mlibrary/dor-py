import typer
import httpx
from typing import Optional
from rich.console import Console
from rich.table import Table

app = typer.Typer()
console = Console()


class AuditError(Exception):
    """
    Custom exception for audit-related errors.
    """

    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message


@app.command()
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

    url = "http://api:8000/api/v1/filesets/status"

    # Define query parameters
    params = {
        "project": project,
        "isid": isid,
        "group_by": group_by,
        "status": status,
    }

    # Remove None values from params
    params = {key: value for key, value in params.items() if value is not None}

    if not params.get("project"):
        raise AuditError("Project is a required parameter.", code=400)

    try:
        # Send the GET request to FastAPI
        response = httpx.get(url, params=params)

        response.raise_for_status()  # Raise exception for HTTP errors

        # Parse the JSON response
        upload_statuses = response.json()

        # Display a title for the output
        console.print(f"Upload status for project '{project}':", style="bold cyan")

        # Render the response in a table format
        if isinstance(upload_statuses, dict):
            for group, items in upload_statuses.items():
                console.print(f"[bold green]Group: {group}[/bold green]")
                render_table(items)
        else:
            render_table(upload_statuses)

        return {"upload_statuses": upload_statuses}

    except AuditError as exc:
        console.print(f"Audit error: {exc}", style="bold white on red")
        raise typer.Exit(1)

    except httpx.RequestError as exc:
        console.print(
            f"An error occurred while making the request: {exc}",
            style="bold white on red",
        )
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
        # Add columns dynamically based on keys in the first item
        for key in items[0].keys():
            table.add_column(key.capitalize())

        # Add rows dynamically based on item values
        for item in items:
            table.add_row(*[str(value) for value in item.values()])

    console.print(table)


# class AuditError(Exception):
#     pass


# @app.command()
# def audit(
#     project: str = typer.Option(..., help="The project name (required)"),
#     isid: Optional[str] = typer.Option(
#         None, help="Delivery/batch ID for a specific check (optional)"
#     ),
#     group_by: Optional[str] = typer.Option(
#         "isid", help="Group results by 'isid', 'date', or 'status' (default: 'isid')"
#     ),
#     status: Optional[str] = typer.Option(
#         None, help="Filter by status (completed, failed, queued, etc.)"
#     ),
# ):
#     url = "http://api:8000/api/v1/filesets/status"

#     # Define query parameters
#     params = {
#         "project": project,
#         "isid": isid,
#         "group_by": group_by,
#         "status": status,
#     }

#     # Remove None values from params
#     params = {key: value for key, value in params.items() if value is not None}

#     if not params.get("project"):
#         raise AuditError("Project is a required parameter.")

#     try:
#         # Send the GET request to FastAPI
#         response = httpx.get(url, params=params)
#         response.raise_for_status()  # Raise exception for HTTP errors

#         # Parse the JSON response
#         upload_statuses = response.json()

#         # Display a title for the output
#         console.print(f"Upload status for project '{project}':", style="bold cyan")

#         # Render the response in a table format
#         if isinstance(upload_statuses, dict):
#             for group, items in upload_statuses.items():
#                 console.print(f"[bold green]Group: {group}[/bold green]")
#                 render_table(items)
#         else:
#             render_table(upload_statuses)

#         return {"upload_statuses": upload_statuses}

#     except AuditError as exc:
#         console.print(f"Audit error: {exc}", style="bold white on red")
#         raise typer.Exit(1)

#     except httpx.RequestError as exc:
#         console.print(
#             f"An error occurred while making the request: {exc}",
#             style="bold white on red",
#         )
#         raise typer.Exit(1)

#     except httpx.HTTPStatusError as exc:
#         handle_http_error(exc, project)


# def render_table(items):
#     """
#     Render a table of upload statuses.
#     """
#     table = Table(show_header=True, header_style="bold magenta")
#     table.add_column("Name", style="dim")
#     table.add_column("Status")
#     table.add_column("Date")

#     for item in items:
#         table.add_row(
#             item.get("name", "N/A"), item.get("status", "N/A"), item.get("date", "N/A")
#         )
#     console.print(table)


# def handle_http_error(exc, project):
#     """
#     Handle HTTP status errors and provide meaningful feedback.
#     """
#     detail = exc.response.json().get("detail", "")
#     if f"Project {project} not found" in detail:
#         console.print(f"Project '{project}' was not found.", style="bold red")
#         raise typer.Exit(1)
#     console.print(
#         f"HTTP error occurred: {exc.response.status_code} - {exc.response.text}",
#         style="bold red",
#     )
#     raise typer.Exit(1)
