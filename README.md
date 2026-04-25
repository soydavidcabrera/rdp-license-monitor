# RDP License Monitor

Herramienta CLI para auditar licencias de Remote Desktop Services (RDS)
en Windows Server. Pensada para consultores IT y SysAdmins que gestionan
múltiples clientes PYME.

## Qué hace

- Consulta packs de CALs y licencias emitidas en un servidor con el rol RD Licensing
- Genera reporte en consola con resumen y detalle
- Exporta a CSV para archivo o análisis posterior
- **Read-only**: nunca modifica la configuración de licencias del servidor

## Requisitos

- **Servidor objetivo:** Windows Server 2016, 2019 o 2022 con el rol RD Licensing instalado
- **Permisos:** usuario local o de dominio con acceso de lectura al namespace WMI `root\CIMV2`
- **Ejecución local:** Python 3.11+
- **Ejecución remota:** WinRM habilitado en el servidor (puerto 5985/5986)

## Instalación

Desde PyPI (cuando esté publicado):
```bash
pip install rdp-license-monitor
```

Desde código fuente:
```bash
git clone https://github.com/soydavidcabrera/rdp-license-monitor.git
cd rdp-license-monitor
pip install -e .
```

## Uso básico

Auditoría local (correr en el license server):
```bash
rdp-license-monitor audit --local
```

Auditoría remota con credenciales actuales (Kerberos):
```bash
rdp-license-monitor audit --server srv-rds01.cliente.local
```

Remota con usuario explícito (pide password):
```bash
rdp-license-monitor audit --server srv-rds01.cliente.local --user CLIENTE\admin
```

Exportar a CSV:
```bash
rdp-license-monitor audit --local --csv ./reporte.csv
```

## Seguridad

- Solo realiza operaciones de lectura sobre WMI
- Las credenciales nunca se loguean ni se guardan en disco
- Para entornos automatizados: usar Service Account con Kerberos y permisos delegados mínimos
- Recomendado: ejecutar desde una workstation de gestión hardenizada, no desde el servidor de producción

## Contribuir

Issues y PRs bienvenidos. Antes de abrir un PR, correr:

```bash
pip install -e ".[dev]"
pre-commit run --all-files
pytest
```

## Licencia

MIT — ver [LICENSE](LICENSE).
