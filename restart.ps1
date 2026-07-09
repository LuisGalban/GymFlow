# GymFlow — Restart Rápido (One-Click)
<#
.SYNOPSIS
    Reinicia GymFlow backend (uvicorn) y frontend (Next.js) con un solo clic.
.DESCRIPTION
    1. git pull (actualiza codigo)
    2. Limpia __pycache__ del backend
    3. Mata proceso en puerto 8000 y reinicia uvicorn
    4. Reconstruye (pnpm build) y reinicia Next.js en puerto 3000
.PARAMETER DryRun
    Solo muestra que se haria, sin ejecutar acciones destructivas.
.EXAMPLE
    .\restart.ps1
    .\restart.ps1 -DryRun
#>

param([switch]$DryRun)

$script:stepCount = 1
$rootDir = $PSScriptRoot

function Write-Step {
    param([string]$Message, [string]$Color = "Yellow")
    Write-Host ""
    Write-Host "[$($script:stepCount)/4] $Message" -ForegroundColor $Color
    $script:stepCount++
}

function Get-ProcessByPort {
    param([int]$Port)
    $line = netstat -ano 2>$null | Select-String "LISTENING.*\b${Port}\b"
    if ($line) {
        $tokens = $line.Line -split '\s+'
        $pid = $tokens[-1]
        if ($pid -match '^\d+$') { return [int]$pid }
    }
    return $null
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   GymFlow: Restart Rapido" -ForegroundColor Cyan
if ($DryRun) {
    Write-Host "   MODO DRY-RUN (solo lectura)" -ForegroundColor Magenta
}
Write-Host "=====================================" -ForegroundColor Cyan

# ----- 1. Git pull -----
Write-Step -Message "Actualizando codigo (git pull)..."
if (-not $DryRun) {
    Push-Location -LiteralPath $rootDir
    git pull
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: git pull fallo. Revisa conflictos manualmente." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Pop-Location
} else {
    Write-Host "  [DRY-RUN] git pull en $rootDir" -ForegroundColor Magenta
}

# ----- 2. Limpiar __pycache__ -----
Write-Step -Message "Limpiando cache de Python..."
if (-not $DryRun) {
    $cacheDirs = Get-ChildItem -Path "$rootDir\backend" -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue
    if ($cacheDirs) {
        $cacheDirs | Remove-Item -Recurse -Force
        Write-Host "  Eliminados $($cacheDirs.Count) directorios __pycache__." -ForegroundColor Green
    } else {
        Write-Host "  No se encontraron __pycache__." -ForegroundColor Green
    }
} else {
    Write-Host "  [DRY-RUN] Get-ChildItem + Remove-Item __pycache__ en backend\" -ForegroundColor Magenta
}

# ----- 3. Reiniciar backend -----
Write-Step -Message "Reiniciando backend (uvicorn)..."
$backendPid = Get-ProcessByPort -Port 8000
if ($backendPid) {
    Write-Host "  Puerto 8000 ocupado por PID $backendPid. Deteniendo..." -ForegroundColor Yellow
    if (-not $DryRun) {
        Stop-Process -Id $backendPid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
} else {
    Write-Host "  Puerto 8000 libre." -ForegroundColor Green
}

if (-not $DryRun) {
    $backendDir = "$rootDir\backend"
    $pythonExe = "$backendDir\venv\Scripts\python.exe"
    if (-not (Test-Path $pythonExe)) {
        Write-Host "ERROR: No se encontro $pythonExe. Verifica que el venv existe." -ForegroundColor Red
        exit 1
    }
    Start-Process -WindowStyle Hidden -FilePath $pythonExe -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload" -WorkingDirectory $backendDir
    Write-Host "  Backend iniciado en http://localhost:8000" -ForegroundColor Green
} else {
    Write-Host "  [DRY-RUN] Start-Process uvicorn app.main:app :8000" -ForegroundColor Magenta
}

# ----- 4. Reconstruir y reiniciar frontend -----
Write-Step -Message "Reconstruyendo y reiniciando frontend (Next.js)..."
if (-not $DryRun) {
    $frontendDir = "$rootDir\frontend"
    Push-Location -LiteralPath $frontendDir

    Write-Host "  Ejecutando pnpm build..." -ForegroundColor Yellow
    pnpm build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: pnpm build fallo." -ForegroundColor Red
        Pop-Location
        exit 1
    }
    Write-Host "  pnpm build completado." -ForegroundColor Green
    Pop-Location
} else {
    Write-Host "  [DRY-RUN] pnpm build en $rootDir\frontend" -ForegroundColor Magenta
}

$frontendPid = Get-ProcessByPort -Port 3000
if ($frontendPid) {
    Write-Host "  Puerto 3000 ocupado por PID $frontendPid. Deteniendo..." -ForegroundColor Yellow
    if (-not $DryRun) {
        Stop-Process -Id $frontendPid -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 1
    }
} else {
    Write-Host "  Puerto 3000 libre." -ForegroundColor Green
}

if (-not $DryRun) {
    $frontendDir = "$rootDir\frontend"
    $pnpmCmd = Get-Command "pnpm" -ErrorAction SilentlyContinue
    if (-not $pnpmCmd) {
        Write-Host "ERROR: pnpm no encontrado en PATH." -ForegroundColor Red
        exit 1
    }
    Start-Process -WindowStyle Hidden -FilePath "pnpm" -ArgumentList "start" -WorkingDirectory $frontendDir
    Write-Host "  Frontend iniciado en http://localhost:3000" -ForegroundColor Green
} else {
    Write-Host "  [DRY-RUN] Start-Process pnpm start" -ForegroundColor Magenta
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "   GymFlow: Restart completado" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Backend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:3000"
