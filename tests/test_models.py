"""Tests de modelos Pydantic."""
from __future__ import annotations

from rdp_license_monitor.core.models import KeyPackStatus, LicenseKeyPack, LicenseType


def make_pack(**kwargs) -> LicenseKeyPack:
    defaults = dict(
        keypack_id=1,
        description="Test CAL",
        product_version="Windows Server 2022",
        license_type=LicenseType.PER_USER,
        total_licenses=100,
        available_licenses=60,
        issued_licenses=40,
        status=KeyPackStatus.ACTIVE,
    )
    return LicenseKeyPack(**{**defaults, **kwargs})


def test_usage_pct_normal():
    kp = make_pack(total_licenses=100, issued_licenses=40)
    assert kp.usage_pct == 40.0


def test_usage_pct_zero_total():
    kp = make_pack(total_licenses=0, issued_licenses=0)
    assert kp.usage_pct == 0.0


def test_usage_pct_full():
    kp = make_pack(total_licenses=50, issued_licenses=50)
    assert kp.usage_pct == 100.0
