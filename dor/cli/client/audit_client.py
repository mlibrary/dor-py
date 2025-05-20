import httpx
from typing import Optional, Any


class AuditError(Exception):
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.code = code

    def __str__(self):
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message


async def fetch_audit_status(
    client: httpx.AsyncClient,
    base_url: str,
    project: str,
    isid: Optional[str] = None,
    group_by: Optional[str] = "isid",
    status: Optional[str] = None,
) -> Any:
    if not project:
        raise AuditError("Project is a required parameter.", code=404)

    params = {
        "project": project,
        "isid": isid,
        "group_by": group_by,
        "status": status,
    }

    params = {k: v for k, v in params.items() if v is not None}
    response = await client.get(f"{base_url}/api/v1/filesets/status", params=params)
    response.raise_for_status()
    return response.json()
