# Gearbox Studio — Validation Script
# Runs backend tests and verifies the generation pipeline

Write-Host "=== Gearbox Studio Validation ===" -ForegroundColor Cyan

$backendDir = Join-Path $PSScriptRoot "..\backend"
$rootDir = Join-Path $PSScriptRoot ".."

# Run calculation tests
Write-Host "`n--- Running calculation tests ---" -ForegroundColor Yellow
Push-Location $backendDir
python -m pytest tests/test_calculations.py -v
$calcResult = $LASTEXITCODE
Pop-Location

# Run CAD tests
Write-Host "`n--- Running CAD tests ---" -ForegroundColor Yellow
Push-Location $backendDir
python -m pytest tests/test_cad.py -v
$cadResult = $LASTEXITCODE
Pop-Location

# Run API tests
Write-Host "`n--- Running API tests ---" -ForegroundColor Yellow
Push-Location $backendDir
python -m pytest tests/test_api.py -v
$apiResult = $LASTEXITCODE
Pop-Location

# Summary
Write-Host "`n=== Validation Summary ===" -ForegroundColor Cyan
Write-Host "Calculation tests: $(if ($calcResult -eq 0) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($calcResult -eq 0) { 'Green' } else { 'Red' })
Write-Host "CAD tests: $(if ($cadResult -eq 0) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($cadResult -eq 0) { 'Green' } else { 'Red' })
Write-Host "API tests: $(if ($apiResult -eq 0) { 'PASSED' } else { 'FAILED' })" -ForegroundColor $(if ($apiResult -eq 0) { 'Green' } else { 'Red' })
