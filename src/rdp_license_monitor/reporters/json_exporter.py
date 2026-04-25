"""Exporter a JSON."""
from __future__ import annotations

import json
from pathlib import Path

from rdp_license_monitor.core.models import AuditReport


def export(report: AuditReport, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = report.model_dump(mode="json")
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
