# Architecture

## Overview

Hybrid Python + PowerShell approach: Python orchestrates collection and reporting; PowerShell scripts handle WMI queries (both embedded and as standalone fallbacks).

## Layers

```
CLI (cli.py)
  └── Collectors (collectors/)    ← run PS scripts via Session
        └── Session (core/connection.py)
              ├── LocalSession    ← subprocess powershell.exe
              └── RemoteSession   ← pypsrp over WSMan
  └── Reporters (reporters/)
        ├── console.py            ← Rich tables
        └── csv_exporter.py
  └── Models (core/models.py)     ← Pydantic, source of truth
```

## Auth flow

1. Default: Kerberos (no credentials needed if running as domain user)
2. Explicit: `--user DOMAIN\user` triggers `getpass()` prompt — password never touches disk or logs
3. Future (v0.3): `keyring` integration for cached credentials

## WMI namespaces used

| Class | Namespace | Purpose |
|-------|-----------|---------|
| `Win32_TSLicenseKeyPack` | `root\CIMV2` | CAL packs installed |
| `Win32_TSIssuedLicense` | `root\CIMV2` | Issued licenses (v0.2) |
