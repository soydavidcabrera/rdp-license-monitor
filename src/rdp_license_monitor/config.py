"""Configuración multi-servidor desde YAML."""
from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator


class ServerConfig(BaseModel):
    name: str
    host: str
    user: str | None = None
    use_kerberos: bool = True


class OutputConfig(BaseModel):
    csv_dir: Path = Path("./reports")
    html_dir: Path | None = None
    filename_pattern: str = "{date}_{server}.csv"

    def _safe_name(self, server_name: str) -> str:
        return server_name.replace(" ", "_").replace("\\", "_").replace("/", "_")

    def resolve_filename(self, server_name: str, date: str) -> Path:
        filename = self.filename_pattern.format(date=date, server=self._safe_name(server_name))
        return self.csv_dir / filename

    def resolve_html_filename(self, server_name: str, date: str) -> Path | None:
        if self.html_dir is None:
            return None
        filename = f"{date}_{self._safe_name(server_name)}.html"
        return self.html_dir / filename


class BatchConfig(BaseModel):
    servers: list[ServerConfig] = Field(min_length=1)
    output: OutputConfig = Field(default_factory=OutputConfig)

    @field_validator("servers")
    @classmethod
    def no_duplicate_hosts(cls, servers: list[ServerConfig]) -> list[ServerConfig]:
        hosts = [s.host for s in servers]
        if len(hosts) != len(set(hosts)):
            raise ValueError("hosts duplicados en la configuración")
        return servers

    @classmethod
    def from_yaml(cls, path: Path) -> "BatchConfig":
        text = Path(path).read_text(encoding="utf-8")
        data = yaml.safe_load(text)
        return cls.model_validate(data)
