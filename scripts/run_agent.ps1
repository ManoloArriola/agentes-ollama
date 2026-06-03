param(
    [string]$agent = "correo"
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $root "..")
$agentPath = Join-Path $repo $agent
if (-Not (Test-Path $agentPath)) { Write-Error "Agente no encontrado: $agent"; exit 1 }

$activate = Join-Path $agentPath "venv\Scripts\Activate.ps1"
if (Test-Path $activate) {
    Write-Host "Activando entorno de $agent..."
    . $activate
} else {
    Write-Host "No se encontró entorno virtual. Ejecuta scripts/setup_envs.ps1 primero.";
    exit 1
}

Write-Host "Ejecutando $agent/main.py"
python (Join-Path $agentPath "main.py")
