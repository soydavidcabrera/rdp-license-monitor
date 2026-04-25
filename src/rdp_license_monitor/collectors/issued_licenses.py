"""Collector de licencias emitidas."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from rdp_license_monitor.core.models import IssuedLicense, LicenseType

if TYPE_CHECKING:
    from rdp_license_monitor.core.connection import Session


PS_QUERY = """
Get-CimInstance -ClassName Win32_TSIssuedLicense |
  Select-Object LicenseId, KeyPackId, sHardwareId, IssuedToUser,
                IssuedToComputer, IssueDate, ExpirationDate, LicenseStatus |
  ConvertTo-Json -Compress -Depth 3
"""

# LicenseStatus: 1=Active, 2=Pending, 4=Concurrent, 5=Expired,
#                6=Revoked, 7=Deleted, 8=Temporary
_DEVICE_STATUSES = {4}  # Concurrent = Per Device


def _parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        # WMI returns ISO-like strings; normalize to UTC
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.astimezone(timezone.utc)
    except (ValueError, AttributeError):
        return None


def collect_issued_licenses(session: Session) -> list[IssuedLicense]:
    raw = session.run_ps(PS_QUERY).strip()
    if not raw:
        return []

    data = json.loads(raw)
    if isinstance(data, dict):
        data = [data]

    licenses: list[IssuedLicense] = []
    for item in data:
        status = item.get("LicenseStatus", 0)
        license_type = LicenseType.PER_DEVICE if status in _DEVICE_STATUSES else LicenseType.PER_USER
        user_or_device = (
            item.get("IssuedToComputer")
            or item.get("IssuedToUser")
            or item.get("sHardwareId")
            or "Unknown"
        )
        licenses.append(
            IssuedLicense(
                license_id=item["LicenseId"],
                keypack_id=item["KeyPackId"],
                sid=item.get("sHardwareId"),
                user_or_device=user_or_device,
                issued_at=_parse_date(item.get("IssueDate")),
                expires_at=_parse_date(item.get("ExpirationDate")),
                license_type=license_type,
            )
        )
    return licenses
