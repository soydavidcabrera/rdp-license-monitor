"""Abstracción de conexión: WMI local o PSRP remoto."""
from __future__ import annotations

import platform
import subprocess
from dataclasses import dataclass
from typing import Protocol

from pypsrp.client import Client


class Session(Protocol):
    def run_ps(self, script: str) -> str: ...


@dataclass(frozen=True)
class ServerTarget:
    host: str
    username: str | None = None
    password: str | None = None
    use_kerberos: bool = True

    @property
    def is_local(self) -> bool:
        return self.host.lower() in {"localhost", "127.0.0.1", platform.node().lower()}


class LocalSession:
    """Ejecución local vía powershell.exe."""

    def run_ps(self, script: str) -> str:
        # script viene de constantes internas del paquete, no de input del usuario
        result = subprocess.run(  # noqa: S603
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        if result.returncode != 0:
            raise RuntimeError(f"PowerShell falló: {result.stderr.strip()}")
        return result.stdout


class RemoteSession:
    """Ejecución remota vía WSMan/PSRP."""

    def __init__(self, target: ServerTarget) -> None:
        if target.is_local:
            raise ValueError("Usar LocalSession para ejecución local")
        self._target = target
        self._client = Client(
            server=target.host,
            username=target.username,
            password=target.password,
            auth="kerberos" if target.use_kerberos else "negotiate",
            ssl=False,  # cambiar a True cuando uses HTTPS WinRM (recomendado)
        )

    def run_ps(self, script: str) -> str:
        stdout, streams, had_errors = self._client.execute_ps(script)
        if had_errors:
            errors = "\n".join(str(e) for e in streams.error)
            raise RuntimeError(f"PowerShell remoto falló: {errors}")
        return stdout
