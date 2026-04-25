#Requires -Version 5.1
<#
.SYNOPSIS
    Audita licencias RDS en un Windows Server con el rol RD Licensing.
.DESCRIPTION
    Script standalone como fallback cuando no se puede instalar Python.
    Read-only: no modifica ninguna configuración del servidor.
.PARAMETER Server
    Nombre o IP del servidor. Omitir para ejecución local.
.EXAMPLE
    .\Get-RDLicenses.ps1
    .\Get-RDLicenses.ps1 -Server srv-rds01.cliente.local
#>
param(
    [string]$Server = "localhost"
)

$query = { Get-CimInstance -ClassName Win32_TSLicenseKeyPack }

if ($Server -ne "localhost") {
    $session = New-CimSession -ComputerName $Server
    $packs = Get-CimInstance -ClassName Win32_TSLicenseKeyPack -CimSession $session
} else {
    $packs = & $query
}

if (-not $packs) {
    Write-Warning "No se encontraron packs de CALs. ¿Está instalado el rol RD Licensing?"
    exit 1
}

$total = ($packs | Measure-Object -Property TotalLicenses -Sum).Sum
$issued = ($packs | Measure-Object -Property IssuedLicenses -Sum).Sum
$available = $total - $issued

Write-Host "`n=== RDS License Audit — $Server ===" -ForegroundColor Cyan
Write-Host "Total CALs : $total"
Write-Host "Emitidas   : $issued"
Write-Host "Disponibles: $available"
Write-Host ""

$packs | Select-Object KeyPackId, Description, ProductVersion,
    TotalLicenses, IssuedLicenses, AvailableLicenses |
    Format-Table -AutoSize
