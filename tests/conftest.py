"""Fixtures compartidos para tests."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from rdp_license_monitor.core.models import AuditReport, KeyPackStatus, LicenseKeyPack, LicenseType

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture()
def sample_key_packs() -> list[LicenseKeyPack]:
    return [
        LicenseKeyPack(
            keypack_id=1,
            description="Windows Server 2022 — RDS Per User CAL",
            product_version="Windows Server 2022",
            license_type=LicenseType.PER_USER,
            total_licenses=50,
            available_licenses=20,
            issued_licenses=30,
            status=KeyPackStatus.ACTIVE,
        ),
    ]


@pytest.fixture()
def sample_report(sample_key_packs: list[LicenseKeyPack]) -> AuditReport:
    return AuditReport(
        server="srv-rds01.test.local",
        key_packs=sample_key_packs,
        issued_licenses=[],
    )


@pytest.fixture()
def wmi_samples() -> dict:
    path = FIXTURES_DIR / "wmi_samples.json"
    return json.loads(path.read_text(encoding="utf-8"))
