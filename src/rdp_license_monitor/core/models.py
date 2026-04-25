"""Modelos Pydantic para entidades de licenciamiento."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class LicenseType(str, Enum):
    PER_USER = "Per User"
    PER_DEVICE = "Per Device"
    UNKNOWN = "Unknown"


class KeyPackStatus(str, Enum):
    ACTIVE = "Active"
    EXPIRED = "Expired"
    REVOKED = "Revoked"
    OTHER = "Other"


class LicenseKeyPack(BaseModel):
    """Pack de CALs instalado en el license server."""

    keypack_id: int
    description: str
    product_version: str
    license_type: LicenseType
    total_licenses: int
    available_licenses: int
    issued_licenses: int
    status: KeyPackStatus
    expiration_date: datetime | None = None

    @property
    def usage_pct(self) -> float:
        if self.total_licenses == 0:
            return 0.0
        return (self.issued_licenses / self.total_licenses) * 100


class IssuedLicense(BaseModel):
    """Licencia emitida a un usuario o dispositivo."""

    license_id: int
    keypack_id: int
    sid: str | None = None
    user_or_device: str
    issued_at: datetime | None = None
    expires_at: datetime | None = None
    license_type: LicenseType


class AuditReport(BaseModel):
    """Resultado completo de auditoría sobre un servidor."""

    server: str
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    key_packs: list[LicenseKeyPack]
    issued_licenses: list[IssuedLicense]

    @property
    def total_cals(self) -> int:
        return sum(kp.total_licenses for kp in self.key_packs)

    @property
    def total_issued(self) -> int:
        return sum(kp.issued_licenses for kp in self.key_packs)
