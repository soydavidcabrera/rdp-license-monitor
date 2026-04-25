"""Tests de collectors con sesión mockeada."""
from __future__ import annotations

import json

import pytest

from rdp_license_monitor.collectors.license_packs import collect_key_packs
from rdp_license_monitor.core.models import LicenseType


class MockSession:
    def __init__(self, response: str) -> None:
        self._response = response

    def run_ps(self, script: str) -> str:  # noqa: ARG002
        return self._response


def test_collect_key_packs_list(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"])
    session = MockSession(payload)
    packs = collect_key_packs(session)
    assert len(packs) == 2
    assert packs[0].license_type == LicenseType.PER_USER
    assert packs[1].license_type == LicenseType.PER_DEVICE


def test_collect_key_packs_single_object(wmi_samples):
    payload = json.dumps(wmi_samples["key_packs"][0])
    session = MockSession(payload)
    packs = collect_key_packs(session)
    assert len(packs) == 1


def test_collect_key_packs_empty():
    session = MockSession("")
    packs = collect_key_packs(session)
    assert packs == []
