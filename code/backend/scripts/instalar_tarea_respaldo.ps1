# Tarea programada del respaldo local (023 · opción B).
#
#   .\instalar_tarea_respaldo.ps1            instala (o actualiza) la tarea: domingos 3:00
#   .\instalar_tarea_respaldo.ps1 -Ahora     corre el respaldo en este momento
#   .\instalar_tarea_respaldo.ps1 -Pausar    deja de respaldar (ej. saltar una semana)
#   .\instalar_tarea_respaldo.ps1 -Reanudar  vuelve a respaldar cada domingo
#   .\instalar_tarea_respaldo.ps1 -Estado    última y próxima corrida
#   .\instalar_tarea_respaldo.ps1 -Quitar    elimina la tarea
#
# Pausar no borra nada: los respaldos de la nube siguen corriendo y, al
# reanudar, la regla de conservación sigue con los respaldos que existan.

param(
    [switch]$Ahora,
    [switch]$Pausar,
    [switch]$Reanudar,
    [switch]$Estado,
    [switch]$Quitar
)

$ErrorActionPreference = 'Stop'
$nombre = 'FleboSil - Respaldo semanal'
$script = Join-Path $PSScriptRoot 'respaldar_local.ps1'

if ($Ahora) { Start-ScheduledTask -TaskName $nombre; Write-Host 'Respaldo iniciado. Revisa respaldos.log en la carpeta de respaldos.'; return }
if ($Pausar) { Disable-ScheduledTask -TaskName $nombre | Out-Null; Write-Host 'Respaldo local en pausa. Reanúdalo con -Reanudar.'; return }
if ($Reanudar) { Enable-ScheduledTask -TaskName $nombre | Out-Null; Write-Host 'Respaldo local reanudado: domingos a las 3:00.'; return }
if ($Quitar) { Unregister-ScheduledTask -TaskName $nombre -Confirm:$false; Write-Host 'Tarea eliminada.'; return }
if ($Estado) {
    $tarea = Get-ScheduledTask -TaskName $nombre
    $info = $tarea | Get-ScheduledTaskInfo
    Write-Host "Estado: $($tarea.State)"
    Write-Host "Última corrida: $($info.LastRunTime) (resultado $($info.LastTaskResult); 0 = sin errores)"
    Write-Host "Próxima corrida: $($info.NextRunTime)"
    return
}

$accion = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$script`""
$disparador = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '03:00'
# Si el equipo estaba apagado a esa hora, corre en cuanto se pueda; espera a
# tener red y despierta al equipo si está suspendido.
$ajustes = New-ScheduledTaskSettingsSet -StartWhenAvailable -RunOnlyIfNetworkAvailable -WakeToRun `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Hours 2)

Register-ScheduledTask -TaskName $nombre -Action $accion -Trigger $disparador -Settings $ajustes `
    -Description 'Respaldo cifrado semanal de la base de FleboSil ERP y copia de las facturas (feature 023).' `
    -Force | Out-Null
Write-Host "Tarea '$nombre' instalada: domingos a las 3:00."
