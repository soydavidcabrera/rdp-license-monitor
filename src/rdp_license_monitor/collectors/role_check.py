"""Verifica si el rol RD Licensing está instalado en el servidor."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rdp_license_monitor.core.connection import Session

PS_QUERY = """
$role = Get-WindowsFeature -Name RDS-Licensing -ErrorAction SilentlyContinue
if ($role) { $role.InstallState.ToString() } else { "NotFound" }
"""


def is_rds_licensing_installed(session: Session) -> bool:
    """Returns True if the RD Licensing role is installed and active."""
    try:
        result = session.run_ps(PS_QUERY).strip()
        return result.lower() == "installed"
    except Exception:
        # If the check itself fails, proceed without blocking the audit
        return False
