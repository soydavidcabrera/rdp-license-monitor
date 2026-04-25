"""Tests de la CLI con Typer test client."""
from __future__ import annotations

from typer.testing import CliRunner

from rdp_license_monitor.cli import app

runner = CliRunner()


def test_audit_requires_server_or_local():
    result = runner.invoke(app, ["audit"])
    assert result.exit_code == 2


def test_audit_help():
    result = runner.invoke(app, ["audit", "--help"])
    assert result.exit_code == 0
    assert "--server" in result.output
    assert "--local" in result.output
