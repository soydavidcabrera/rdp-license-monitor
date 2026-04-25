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
                KeyPackType, ExpirationDate |
  ConvertTo-Json -Compress -Depth 3
"""

# Valores de KeyPackType según docs WMI de Microsoft:
# 0=Unknown, 1=Retail, 2=Volume, 3=Concurrent, 4=Temporary, 5=OpenLicense, 6=BuiltIn
_TYPE_MAP = {
    2: LicenseType.PER_DEVICE,
    4: LicenseType.PER_USER,
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
        packs.append(
            LicenseKeyPack(
                keypack_id=item["KeyPackId"],
                description=item.get("Description") or "",
                product_version=item.get("ProductVersion") or "",
                license_type=_TYPE_MAP.get(kp_type, LicenseType.UNKNOWN),
                total_licenses=item.get("TotalLicenses", 0),
                available_licenses=item.get("AvailableLicenses", 0),
                issued_licenses=item.get("IssuedLicenses", 0),
                status=KeyPackStatus.ACTIVE,  # refinar con KeyPackStatus real en v0.2
                expiration_date=None,
            )
        )
    return packs
