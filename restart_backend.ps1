# Restart Backend Server Script
# This will stop the old backend and start a new one with updated code

Write-Host "=== SpecSentinel Backend Restart ===" -ForegroundColor Cyan
Write-Host ""

# Find and stop the backend process on port 8000
Write-Host "1. Checking for backend server on port 8000..." -ForegroundColor Yellow
$port8000 = netstat -ano | findstr ":8000" | findstr "LISTENING"
if ($port8000) {
    $processId = ($port8000 -split '\s+')[-1]
    Write-Host "   Found backend server (PID: $processId)" -ForegroundColor Green
    Write-Host "   Stopping old backend server..." -ForegroundColor Yellow
    Stop-Process -Id $processId -Force
    Start-Sleep -Seconds 2
    Write-Host "   OK Old backend stopped" -ForegroundColor Green
} else {
    Write-Host "   No backend server found on port 8000" -ForegroundColor Gray
}

Write-Host ""
Write-Host "2. Starting new backend server with updated code..." -ForegroundColor Yellow
Write-Host "   Running: python run_app.py" -ForegroundColor Gray
Write-Host ""
Write-Host "=== Backend Server Starting ===" -ForegroundColor Cyan
Write-Host "Wait for: Uvicorn running on http://0.0.0.0:8000" -ForegroundColor Green
Write-Host ""

# Start the backend
python run_app.py

# Made with Bob
