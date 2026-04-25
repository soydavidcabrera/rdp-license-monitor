"""Tests de exporters JSON y HTML."""
from __future__ import annotations

import json

from rich.console import Console

from rdp_license_monitor.reporters import console as console_reporter
from rdp_license_monitor.reporters import html_reporter, json_exporter


# --- JSON exporter ---

def test_json_export_valid(tmp_path, sample_report):
    out = tmp_path / "report.json"
    json_exporter.export(sample_report, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["server"] == "srv-rds01.test.local"
    assert "key_packs" in data
    assert "issued_licenses" in data
    assert len(data["key_packs"]) == 1
    assert data["key_packs"][0]["keypack_id"] == 1


def test_json_export_creates_parent_dirs(tmp_path, sample_report):
    out = tmp_path / "nested" / "deep" / "report.json"
    json_exporter.export(sample_report, out)
    assert out.exists()


def test_json_export_fields(tmp_path, sample_report):
    out = tmp_path / "report.json"
    json_exporter.export(sample_report, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    kp = data["key_packs"][0]
    assert kp["total_licenses"] == 50
    assert kp["issued_licenses"] == 30
    assert kp["license_type"] == "Per User"
    assert kp["status"] == "Active"


def test_json_export_grace_period(tmp_path, grace_period_report):
    out = tmp_path / "grace.json"
    json_exporter.export(grace_period_report, out)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["key_packs"] == []
    assert data["issued_licenses"] == []


# --- HTML exporter ---

def test_html_export_creates_file(tmp_path, sample_report):
    out = tmp_path / "report.html"
    html_reporter.export(sample_report, out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_html_export_contains_server_name(tmp_path, sample_report):
    out = tmp_path / "report.html"
    html_reporter.export(sample_report, out)
    content = out.read_text(encoding="utf-8")
    assert "srv-rds01.test.local" in content


def test_html_export_contains_metrics(tmp_path, sample_report):
    out = tmp_path / "report.html"
    html_reporter.export(sample_report, out)
    content = out.read_text(encoding="utf-8")
    assert "50" in content     # total_licenses
    assert "30" in content     # issued_licenses
    assert "60.0%" in content  # usage_pct


def test_html_export_creates_parent_dirs(tmp_path, sample_report):
    out = tmp_path / "sub" / "report.html"
    html_reporter.export(sample_report, out)
    assert out.exists()


def test_html_export_grace_period_no_exception(tmp_path, grace_period_report):
    out = tmp_path / "grace.html"
    html_reporter.export(grace_period_report, out)
    assert out.exists()


def test_html_export_grace_period_shows_warning(tmp_path, grace_period_report):
    out = tmp_path / "grace.html"
    html_reporter.export(grace_period_report, out)
    content = out.read_text(encoding="utf-8")
    assert "grace period" in content.lower()
    assert "srv-grace.test.local" in content


# --- Console reporter ---

def test_console_render_grace_period_no_exception(grace_period_report):
    console = Console(file=open("/dev/null", "w"))  # noqa: SIM115
    console_reporter.render(grace_period_report, console=console)


def test_console_render_grace_period_shows_warning(grace_period_report, capsys):
    console = Console(highlight=False)
    console_reporter.render(grace_period_report, console=console)
    captured = capsys.readouterr()
    assert "grace period" in captured.out.lower() or "not installed" in captured.out.lower()
