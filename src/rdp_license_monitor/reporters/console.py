"""Reporter de consola con Rich."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from rdp_license_monitor.core.models import AuditReport

_NO_PACKS_MSG = (
    "No license key packs found.\n"
    "Server may be in grace period or RD Licensing role is not installed."
)
_NO_ISSUED_MSG = "No issued licenses found."


def render(report: AuditReport, console: Console | None = None) -> None:
    console = console or Console()

    console.rule(f"[bold]RDS License Audit — {report.server}")
    console.print(f"Collected: {report.collected_at.isoformat()}", style="dim")
    console.print(
        f"Total CALs: [bold]{report.total_cals}[/]  "
        f"Issued: [bold yellow]{report.total_issued}[/]  "
        f"Available: [bold green]{report.total_cals - report.total_issued}[/]"
    )

    if not report.key_packs:
        console.print(Panel(_NO_PACKS_MSG, title="License Key Packs", border_style="yellow"))
        return

    table = Table(title="License Key Packs", show_lines=True)
    table.add_column("ID", justify="right")
    table.add_column("Description")
    table.add_column("Type")
    table.add_column("Total", justify="right")
    table.add_column("Issued", justify="right")
    table.add_column("Available", justify="right")
    table.add_column("Usage %", justify="right")
    table.add_column("Status")

    for kp in report.key_packs:
        color = "green" if kp.usage_pct < 80 else "yellow" if kp.usage_pct < 95 else "red"
        table.add_row(
            str(kp.keypack_id),
            kp.description,
            kp.license_type.value,
            str(kp.total_licenses),
            str(kp.issued_licenses),
            str(kp.available_licenses),
            f"[{color}]{kp.usage_pct:.1f}%[/]",
            kp.status.value,
        )

    console.print(table)

    if not report.issued_licenses:
        console.print(Panel(_NO_ISSUED_MSG, title="Issued Licenses", border_style="dim"))
