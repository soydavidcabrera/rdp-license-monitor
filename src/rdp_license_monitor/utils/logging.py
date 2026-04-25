"""Configuración de logging estructurado."""
from __future__ import annotations

import logging


def setup(level: str = "WARNING") -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        level=getattr(logging, level.upper(), logging.WARNING),
    )
