# Gearbox Studio — Start Script
# Launches both the FastAPI backend and Next.js frontend

Write-Host "=== Gearbox Studio Starting ===" -ForegroundColor Cyan

$rootDir = Join-Path $PSScriptRoot ".."
$backendDir = Join-Path $rootDir "backend"
$frontendDir = Join-Path $rootDir "frontend"

# Start backend
Write-Host "`n--- Starting FastAPI backend (port 8000) ---" -ForegroundColor Yellow
$backend = Start-Process -FilePath "python" -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" -WorkingDirectory $backendDir -PassThru -WindowStyle Normal
Write-Host "Backend PID: $($backend.Id)" -ForegroundColor Green
Write-Host "Backend API: http://127.0.0.1:8000/docs" -ForegroundColor White

# Wait for backend to start
Start-Sleep -Seconds 3

# Start frontend
Write-Host "`n--- Starting Next.js frontend (port 3000) ---" -ForegroundColor Yellow
$frontend = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory $frontendDir -PassThru -WindowStyle Normal
Write-Host "Frontend PID: $($frontend.Id)" -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White

Write-Host "`n=== Both services starting ===" -ForegroundColor Cyan
Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "`nPress Ctrl+C to stop both services" -ForegroundColor White
