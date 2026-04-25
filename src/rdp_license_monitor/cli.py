"""Punto de entrada CLI."""
from __future__ import annotations

from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from rdp_license_monitor.collectors.issued_licenses import collect_issued_licenses
from rdp_license_monitor.collectors.license_packs import collect_key_packs
from rdp_license_monitor.collectors.role_check import is_rds_licensing_installed
from rdp_license_monitor.config import BatchConfig
from rdp_license_monitor.core.connection import (
    LocalSession,
    RemoteSession,
    ServerTarget,
    Session,
)
from rdp_license_monitor.core.models import AuditReport
from rdp_license_monitor.reporters import console as console_reporter
from rdp_license_monitor.reporters import csv_exporter, html_reporter, json_exporter

app = typer.Typer(help="Auditar licencias RDS en Windows Server.", no_args_is_help=True)
err_console = Console(stderr=True)


def _build_session(host: str, user: str | None, use_kerberos: bool) -> tuple[Session, str]:
    password = getpass(f"Password para {user}@{host}: ") if user else None
    target = ServerTarget(host=host, username=user, password=password, use_kerberos=use_kerberos)
    return RemoteSession(target), host


@app.command()
def audit(
    server: str | None = typer.Option(None, "--server", "-s", help="Servidor objetivo"),
    local: bool = typer.Option(False, "--local", help="Forzar ejecución local"),
    user: str | None = typer.Option(None, "--user", "-u", help="Usuario (DOMINIO\\user)"),
    csv_out: Path | None = typer.Option(None, "--csv", help="Exportar a CSV"),
    json_out: Path | None = typer.Option(None, "--json", help="Exportar a JSON"),
    html_out: Path | None = typer.Option(None, "--html", help="Exportar a HTML"),
) -> None:
    """Ejecuta auditoría de licencias RDS en un servidor."""
    if not server and not local:
        err_console.print("[red]error:[/] especificar --server o --local")
        raise typer.Exit(2)

    session: Session
    if local or not server:
        session = LocalSession()
        target_name = "localhost"
    else:
        session, target_name = _build_session(server, user, use_kerberos=True)

    if not is_rds_licensing_installed(session):
        err_console.print(
            "[yellow]warning:[/] RD Licensing role not installed — "
            "server may be in grace period"
        )

    try:
        key_packs = collect_key_packs(session)
        issued_licenses = collect_issued_licenses(session)
    except Exception as exc:
        err_console.print(f"[red]error:[/] {exc}")
        raise typer.Exit(1) from exc

    report = AuditReport(
        server=target_name,
        collected_at=datetime.now(timezone.utc),
        key_packs=key_packs,
        issued_licenses=issued_licenses,
    )

    console_reporter.render(report)
    console = Console()

    if csv_out:
        csv_exporter.export(report, csv_out)
        console.print(f"[green]CSV →[/] {csv_out}")
    if json_out:
        json_exporter.export(report, json_out)
        console.print(f"[green]JSON →[/] {json_out}")
    if html_out:
        html_reporter.export(report, html_out)
        console.print(f"[green]HTML →[/] {html_out}")


@app.command()
def batch(
    config_path: Path = typer.Option(..., "--config", "-c", help="Archivo YAML de servidores"),
) -> None:
    """Audita múltiples servidores definidos en un archivo YAML."""
    try:
        cfg = BatchConfig.from_yaml(config_path)
    except Exception as exc:
        err_console.print(f"[red]error cargando config:[/] {exc}")
        raise typer.Exit(2) from exc

    console = Console()
    date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
    results: list[tuple[str, AuditReport | None, str]] = []

    with Progress(SpinnerColumn(), TextColumn("{task.description}"), console=console) as progress:
        for srv in cfg.servers:
            task = progress.add_task(f"Conectando a [bold]{srv.name}[/]...", total=None)
            try:
                session, _ = _build_session(srv.host, srv.user, srv.use_kerberos)
                key_packs = collect_key_packs(session)
                issued = collect_issued_licenses(session)
                report = AuditReport(
                    server=srv.name,
                    collected_at=datetime.now(timezone.utc),
                    key_packs=key_packs,
                    issued_licenses=issued,
                )
                csv_exporter.export(report, cfg.output.resolve_filename(srv.name, date_str))
                html_path = cfg.output.resolve_html_filename(srv.name, date_str)
                if html_path:
                    html_reporter.export(report, html_path)
                results.append((srv.name, report, ""))
                progress.update(task, description=f"[green]✓[/] {srv.name}")
            except Exception as exc:
                results.append((srv.name, None, str(exc)))
                progress.update(task, description=f"[red]✗[/] {srv.name}: {exc}")

    _render_batch_summary(console, results, cfg.output)


def _render_batch_summary(
    console: Console,
    results: list[tuple[str, AuditReport | None, str]],
    output: object,
) -> None:
    console.rule("[bold]Resumen batch")

    table = Table(show_lines=True)
    table.add_column("Servidor")
    table.add_column("Total CALs", justify="right")
    table.add_column("Emitidas", justify="right")
    table.add_column("Disponibles", justify="right")
    table.add_column("Uso %", justify="right")
    table.add_column("Estado")

    ok = errors = 0
    for name, report, error in results:
        if report is None:
            table.add_row(name, "—", "—", "—", "—", f"[red]{error}[/]")
            errors += 1
            continue

        ok += 1
        total = report.total_cals
        issued = report.total_issued
        avail = total - issued
        pct = (issued / total * 100) if total else 0.0
        color = "green" if pct < 80 else "yellow" if pct < 95 else "red"
        alert = " [yellow]⚠ >80%[/]" if pct >= 80 else ""
        table.add_row(
            name,
            str(total),
            str(issued),
            str(avail),
            f"[{color}]{pct:.1f}%[/]",
            f"[green]OK[/]{alert}",
        )

    console.print(table)
    console.print(f"\n[bold]{ok}[/] servidores OK, [bold]{errors}[/] errores.")


if __name__ == "__main__":
    app()
