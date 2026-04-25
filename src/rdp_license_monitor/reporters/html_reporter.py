"""Exporter a HTML via Jinja2."""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from rdp_license_monitor.core.models import AuditReport
from rdp_license_monitor import __version__

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def _usage_color(pct: float) -> str:
    if pct < 80:
        return "#22c55e"   # green
    if pct < 95:
        return "#f59e0b"   # amber
    return "#ef4444"       # red


def export(report: AuditReport, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=select_autoescape(["html"]),
    )
    env.filters["usage_color"] = _usage_color

    template = env.get_template("report.html.j2")
    html = template.render(report=report, version=__version__)
    path.write_text(html, encoding="utf-8")
