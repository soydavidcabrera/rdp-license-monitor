"""Tests de collectors con sesión mockeada."""
from __future__ import annotations

import json

from rdp_license_monitor.collectors.issued_licenses import collect_issued_licenses
from rdp_license_monitor.collectors.license_packs import collect_key_packs
from rdp_license_monitor.core.models import KeyPackStatus, LicenseType


class MockSession:
    def __init__(self, response: str) -> None:
        self._response = response

    def run_ps(self, script: str) -> str:  # noqa: ARG002
        return self._response


# --- license_packs ---

def test_collect_key_packs_list(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"])
    packs = collect_key_packs(MockSession(payload))
    assert len(packs) == 3
    assert packs[0].license_type == LicenseType.PER_USER
    assert packs[1].license_type == LicenseType.PER_DEVICE


def test_collect_key_packs_single_object(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"][0])
    packs = collect_key_packs(MockSession(payload))
    assert len(packs) == 1


def test_collect_key_packs_empty():
    packs = collect_key_packs(MockSession(""))
    assert packs == []


def test_key_pack_status_active(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"][0])  # KeyPackStatus=0
    packs = collect_key_packs(MockSession(payload))
    assert packs[0].status == KeyPackStatus.ACTIVE


def test_key_pack_status_expired(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"][1])  # KeyPackStatus=1
    packs = collect_key_packs(MockSession(payload))
    assert packs[0].status == KeyPackStatus.EXPIRED


def test_key_pack_status_revoked(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"][2])  # KeyPackStatus=2
    packs = collect_key_packs(MockSession(payload))
    assert packs[0].status == KeyPackStatus.REVOKED


def test_key_pack_type_unknown_for_unmapped(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"][2])  # KeyPackType=99
    packs = collect_key_packs(MockSession(payload))
    assert packs[0].license_type == LicenseType.UNKNOWN


# --- issued_licenses ---

def test_collect_issued_licenses_list(wmi_samples):
    payload = json.dumps(wmi_samples["issued_licenses"])
    licenses = collect_issued_licenses(MockSession(payload))
    assert len(licenses) == 2


def test_issued_license_per_user(wmi_samples):
    payload = json.dumps(wmi_samples["issued_licenses"][0])  # LicenseStatus=1
    licenses = collect_issued_licenses(MockSession(payload))
    assert licenses[0].license_type == LicenseType.PER_USER
    assert licenses[0].user_or_device == "DOMAIN\\jdoe"


def test_issued_license_per_device(wmi_samples):
    payload = json.dumps(wmi_samples["issued_licenses"][1])  # LicenseStatus=4
    licenses = collect_issued_licenses(MockSession(payload))
    assert licenses[0].license_type == LicenseType.PER_DEVICE
    assert licenses[0].user_or_device == "WKST-01"


def test_collect_issued_licenses_empty():
    licenses = collect_issued_licenses(MockSession(""))
    assert licenses == []
