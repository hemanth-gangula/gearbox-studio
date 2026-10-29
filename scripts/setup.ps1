# Gearbox Studio — Setup Script
# Installs Python and Node.js dependencies for local development

Write-Host "=== Gearbox Studio Setup ===" -ForegroundColor Cyan

# Backend dependencies
Write-Host "`n--- Installing Python backend dependencies ---" -ForegroundColor Yellow
$backendDir = Join-Path $PSScriptRoot "..\backend"
pip install -r (Join-Path $backendDir "requirements.txt")
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install backend dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "Backend dependencies installed" -ForegroundColor Green

# Frontend dependencies
Write-Host "`n--- Installing frontend Node.js dependencies ---" -ForegroundColor Yellow
$frontendDir = Join-Path $PSScriptRoot "..\frontend"
Push-Location $frontendDir
npm install
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install frontend dependencies" -ForegroundColor Red
    Pop-Location
    exit 1
}
Pop-Location
Write-Host "Frontend dependencies installed" -ForegroundColor Green

# Create projects directory
$projectsDir = Join-Path $PSScriptRoot "..\projects"
if (-not (Test-Path $projectsDir)) {
    New-Item -ItemType Directory -Path $projectsDir -Force | Out-Null
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "Run .\scripts\start.ps1 to launch the application" -ForegroundColor White
