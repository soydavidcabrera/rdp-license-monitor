"""Collector de packs de CALs instalados."""
from __future__ import annotations

import json
from typing import TYPE_CHECKING

from rdp_license_monitor.core.models import KeyPackStatus, LicenseKeyPack, LicenseType

if TYPE_CHECKING:
    from rdp_license_monitor.core.connection import Session


PS_QUERY = """
Get-CimInstance -ClassName Win32_TSLicenseKeyPack |
  Select-Object KeyPackId, Description, ProductVersion, TypeAndModel,
                TotalLicenses, AvailableLicenses, IssuedLicenses,
                KeyPackType, KeyPackStatus, ExpirationDate |
  ConvertTo-Json -Compress -Depth 3
"""

# KeyPackType values per WMI docs:
# 0=Unknown, 1=Retail (Per Device), 2=Volume (Per Device), 4=Concurrent (Per User),
# 5=Temporary, 6=Open License, 7=Built-in
_TYPE_MAP: dict[int, LicenseType] = {
    1: LicenseType.PER_DEVICE,
    2: LicenseType.PER_DEVICE,
    4: LicenseType.PER_USER,
}

# KeyPackStatus values per WMI docs: 0=Active, 1=Expired, 2=Revoked, 3=Unknown
_STATUS_MAP: dict[int, KeyPackStatus] = {
    0: KeyPackStatus.ACTIVE,
    1: KeyPackStatus.EXPIRED,
    2: KeyPackStatus.REVOKED,
}


def collect_key_packs(session: Session) -> list[LicenseKeyPack]:
    raw = session.run_ps(PS_QUERY).strip()
    if not raw:
        return []

    data = json.loads(raw)
    if isinstance(data, dict):
        data = [data]

    packs: list[LicenseKeyPack] = []
    for item in data:
        kp_type = item.get("KeyPackType", 0)
        kp_status = item.get("KeyPackStatus", 3)
        packs.append(
            LicenseKeyPack(
                keypack_id=item["KeyPackId"],
                description=item.get("Description") or "",
                product_version=item.get("ProductVersion") or "",
                license_type=_TYPE_MAP.get(kp_type, LicenseType.UNKNOWN),
                total_licenses=item.get("TotalLicenses", 0),
                available_licenses=item.get("AvailableLicenses", 0),
                issued_licenses=item.get("IssuedLicenses", 0),
                status=_STATUS_MAP.get(kp_status, KeyPackStatus.OTHER),
                expiration_date=None,
            )
        )
    return packs
