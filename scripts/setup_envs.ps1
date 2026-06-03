<#
Script para crear entornos virtuales por agente e instalar dependencias.
Uso: Ejecutar en PowerShell desde la carpeta del repo:
    .\scripts\setup_envs.ps1
#>
$agents = @("correo", "archivos", "facturacion")
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..")

foreach ($agent in $agents) {
    $agentPath = Join-Path $repo $agent
    if (-Not (Test-Path $agentPath)) {
        Write-Host "Saltando agente inexistente: $agent"
        continue
    }

    $venvPath = Join-Path $agentPath "venv"
    if (-Not (Test-Path $venvPath)) {
        Write-Host "Creando virtualenv para $agent..."
        python -m venv $venvPath
    } else {
        Write-Host "Virtualenv ya existe para $agent."
    }

    $pip = Join-Path $venvPath "Scripts\pip.exe"
    $reqFile = Join-Path $repo (Join-Path "requirements" ("$agent.txt"))
    if ((Test-Path $pip) -and (Test-Path $reqFile)) {
        Write-Host "Instalando dependencias para $agent desde $reqFile..."
        & $pip install --upgrade pip
        & $pip install -r $reqFile
    } else {
        Write-Host "No se encontró pip o requirements para $agent. Pip: $pip, Req: $reqFile"
    }
}

Write-Host "Listo. Activa el entorno con: .\venv\Scripts\Activate.ps1 dentro de la carpeta del agente."
