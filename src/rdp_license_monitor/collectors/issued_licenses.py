"""Collector de licencias emitidas (v0.2)."""
from __future__ import annotations

from typing import TYPE_CHECKING

from rdp_license_monitor.core.models import IssuedLicense

if TYPE_CHECKING:
    from rdp_license_monitor.core.connection import Session


def collect_issued_licenses(session: Session) -> list[IssuedLicense]:  # noqa: ARG001
    # Implementación completa en v0.2
    return []
