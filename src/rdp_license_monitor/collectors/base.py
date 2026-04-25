"""Protocolo base para collectors."""
from __future__ import annotations

from typing import Protocol, TypeVar

T = TypeVar("T")


class Collector(Protocol[T]):
    def collect(self) -> list[T]: ...
