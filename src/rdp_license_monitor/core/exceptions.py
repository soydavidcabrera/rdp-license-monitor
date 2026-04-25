"""Excepciones del dominio."""
from __future__ import annotations


class RDPMonitorError(Exception):
    """Base para todas las excepciones del paquete."""


class ConnectionError(RDPMonitorError):
    """Fallo al conectar con el servidor objetivo."""


class CollectionError(RDPMonitorError):
    """Fallo al recolectar datos WMI."""
