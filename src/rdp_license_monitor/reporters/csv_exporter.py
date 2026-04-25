"""Exporter a CSV."""
from __future__ import annotations

import csv
from pathlib import Path

from rdp_license_monitor.core.models import AuditReport


def export(report: AuditReport, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow([
            "server", "collected_at", "keypack_id", "description",
            "license_type", "total", "issued", "available",
            "usage_pct", "status",
        ])
        for kp in report.key_packs:
            writer.writerow([
                report.server,
                report.collected_at.isoformat(),
                kp.keypack_id,
                kp.description,
                kp.license_type.value,
                kp.total_licenses,
                kp.issued_licenses,
                kp.available_licenses,
                f"{kp.usage_pct:.2f}",
                kp.status.value,
            ])
