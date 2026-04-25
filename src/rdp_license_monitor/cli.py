"""Punto de entrada CLI."""
from __future__ import annotations

from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

import typer
from rich.console import Console

from rdp_license_monitor.collectors.license_packs import collect_key_packs
from rdp_license_monitor.core.connection import (
    LocalSession,
    RemoteSession,
    ServerTarget,
    Session,
)
from rdp_license_monitor.core.models import AuditReport
from rdp_license_monitor.reporters import console as console_reporter
from rdp_license_monitor.reporters import csv_exporter

app = typer.Typer(help="Auditar licencias RDS en Windows Server.", no_args_is_help=True)
err_console = Console(stderr=True)


@app.command()
def audit(
    server: str | None = typer.Option(None, "--server", "-s", help="Servidor objetivo"),
    local: bool = typer.Option(False, "--local", help="Forzar ejecución local"),
    user: str | None = typer.Option(None, "--user", "-u", help="Usuario (DOMINIO\\user)"),
    csv_out: Path | None = typer.Option(None, "--csv", help="Path para exportar CSV"),
) -> None:
    """Ejecuta auditoría de licencias RDS."""
    if not server and not local:
        err_console.print("[red]error:[/] especificar --server o --local")
        raise typer.Exit(2)

    session: Session
    if local or not server:
        session = LocalSession()
        target_name = "localhost"
    else:
        password = getpass(f"Password para {user}: ") if user else None
        target = ServerTarget(host=server, username=user, password=password)
        session = RemoteSession(target)
        target_name = server

    try:
        key_packs = collect_key_packs(session)
    except Exception as exc:
        err_console.print(f"[red]error:[/] {exc}")
        raise typer.Exit(1) from exc

    report = AuditReport(
        server=target_name,
        collected_at=datetime.now(timezone.utc),
        key_packs=key_packs,
        issued_licenses=[],
    )

    console_reporter.render(report)

    if csv_out:
        csv_exporter.export(report, csv_out)
        Console().print(f"[green]CSV escrito en[/] {csv_out}")


if __name__ == "__main__":
    app()
