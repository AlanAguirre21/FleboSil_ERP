# Respaldo semanal en este equipo (023 · opción B).
#
# Lee `code/backend/.env.respaldo`, respalda la base de Railway cifrada en
# RESPALDO_CARPETA (con la misma regla de conservación que la nube) y descarga
# de R2 las facturas que falten. Deja todo en RESPALDO_CARPETA\respaldos.log.
# La tarea programada lo corre los domingos a las 3:00
# (ver `instalar_tarea_respaldo.ps1`); también se puede correr a mano.

$ErrorActionPreference = 'Stop'
$backend = Split-Path -Parent $PSScriptRoot
$archivoEnv = Join-Path $backend '.env.respaldo'

if (-not (Test-Path $archivoEnv)) {
    throw "No existe $archivoEnv. Copia .env.respaldo.example a .env.respaldo y llénalo."
}

# Variables de .env.respaldo solo para este proceso (tienen prioridad sobre .env).
foreach ($linea in Get-Content -Path $archivoEnv -Encoding UTF8) {
    $linea = $linea.Trim()
    if ($linea -eq '' -or $linea.StartsWith('#') -or -not $linea.Contains('=')) { continue }
    $partes = $linea.Split('=', 2)
    [Environment]::SetEnvironmentVariable($partes[0].Trim(), $partes[1].Trim(), 'Process')
}

$python = $env:PYTHON
$carpeta = $env:RESPALDO_CARPETA
if (-not $python -or -not (Test-Path $python)) { throw 'PYTHON en .env.respaldo no apunta a python.exe.' }
if (-not $carpeta) { throw 'Falta RESPALDO_CARPETA en .env.respaldo.' }
New-Item -ItemType Directory -Force -Path $carpeta | Out-Null
$registro = Join-Path $carpeta 'respaldos.log'

function Escribir([string]$texto) {
    $marca = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
    foreach ($renglon in ($texto -split "`r?`n")) {
        if ($renglon.Trim()) { Add-Content -Path $registro -Value "$marca  $renglon" -Encoding UTF8 }
    }
}

function Correr([string]$descripcion, [string[]]$argumentos) {
    # Los comandos de Django escriben en stderr; en PowerShell 5.1 eso no debe
    # cortar el script, solo el código de salida cuenta.
    $ErrorActionPreference = 'Continue'
    $salida = & $python manage.py @argumentos 2>&1 | ForEach-Object { "$_" }
    $codigo = $LASTEXITCODE
    Escribir ("$descripcion`n" + ($salida -join "`n"))
    if ($codigo -ne 0) { Escribir "$descripcion terminó con error (código $codigo)." }
    return $codigo
}

$env:PYTHONIOENCODING = 'utf-8'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Set-Location $backend

Escribir '=== Respaldo semanal ==='
$fallos = 0
if ((Correr 'Base de datos:' @('respaldar', '--destino', 'local')) -ne 0) { $fallos++ }
if ((Correr 'Facturas:' @('subir_facturas_pendientes', '--descargar')) -ne 0) { $fallos++ }
Escribir $(if ($fallos) { "Terminó con $fallos error(es)." } else { 'Terminó sin errores.' })
exit $fallos
