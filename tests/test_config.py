"""Tests de carga y validación de BatchConfig."""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from rdp_license_monitor.config import BatchConfig


def write_yaml(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "servers.yml"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def test_load_valid_config(tmp_path):
    cfg_file = write_yaml(tmp_path, """
        servers:
          - name: "Cliente A"
            host: srv-rds01.clientea.local
            use_kerberos: true
          - name: "Cliente B"
            host: 192.168.10.5
            use_kerberos: false
        output:
          csv_dir: ./reports
          filename_pattern: "{date}_{server}.csv"
    """)
    cfg = BatchConfig.from_yaml(cfg_file)
    assert len(cfg.servers) == 2
    assert cfg.servers[0].name == "Cliente A"
    assert cfg.servers[1].use_kerberos is False
    assert cfg.output.csv_dir == Path("./reports")


def test_load_minimal_config(tmp_path):
    cfg_file = write_yaml(tmp_path, """
        servers:
          - name: "Solo uno"
            host: srv.local
    """)
    cfg = BatchConfig.from_yaml(cfg_file)
    assert len(cfg.servers) == 1
    assert cfg.servers[0].use_kerberos is True
    assert cfg.output.csv_dir == Path("./reports")


def test_missing_servers_key(tmp_path):
    cfg_file = write_yaml(tmp_path, """
        output:
          csv_dir: ./reports
    """)
    with pytest.raises(Exception):
        BatchConfig.from_yaml(cfg_file)


def test_empty_servers_list(tmp_path):
    cfg_file = write_yaml(tmp_path, """
        servers: []
    """)
    with pytest.raises(Exception):
        BatchConfig.from_yaml(cfg_file)


def test_duplicate_hosts_rejected(tmp_path):
    cfg_file = write_yaml(tmp_path, """
        servers:
          - name: "A"
            host: same.host.local
          - name: "B"
            host: same.host.local
    """)
    with pytest.raises(Exception, match="duplicados"):
        BatchConfig.from_yaml(cfg_file)


def test_resolve_filename(tmp_path):
    cfg_file = write_yaml(tmp_path, """
        servers:
          - name: "Cliente A"
            host: srv.local
        output:
          csv_dir: ./reports
          filename_pattern: "{date}_{server}.csv"
    """)
    cfg = BatchConfig.from_yaml(cfg_file)
    path = cfg.output.resolve_filename("Cliente A - RDS01", "20260424")
    assert path == Path("./reports/20260424_Cliente_A_-_RDS01.csv")
