# Start SpecSentinel with Full Logging
# This script starts both backend and frontend with verbose logging to terminal

Write-Host "=" * 70
Write-Host "Starting SpecSentinel with Full Logging"
Write-Host "=" * 70
Write-Host ""

# Set environment variables for verbose logging
$env:LOG_LEVEL = "DEBUG"
$env:FILE_LOGGING = "true"
$env:USE_MULTI_AGENT = "true"

Write-Host "Environment Configuration:"
Write-Host "  LOG_LEVEL: DEBUG (verbose)"
Write-Host "  FILE_LOGGING: true"
Write-Host "  USE_MULTI_AGENT: true"
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] Python found: $pythonVersion"
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+"
    exit 1
}

Write-Host ""
Write-Host "=" * 70
Write-Host "Starting Backend Server (Port 8000)"
Write-Host "=" * 70
Write-Host ""

# Start backend in a new window with full logging
Start-Process powershell -ArgumentList @"
    -NoExit
    -Command
    `$env:LOG_LEVEL='DEBUG';
    `$env:FILE_LOGGING='true';
    `$env:USE_MULTI_AGENT='true';
    Write-Host '========================================';
    Write-Host 'BACKEND SERVER - Port 8000';
    Write-Host '========================================';
    Write-Host '';
    python src/api/app.py
"@

Write-Host "[OK] Backend starting in new window..."
Write-Host ""

# Wait a bit for backend to start
Start-Sleep -Seconds 3

Write-Host "=" * 70
Write-Host "Starting Frontend Server (Port 5000)"
Write-Host "=" * 70
Write-Host ""

# Start frontend in a new window with full logging
Start-Process powershell -ArgumentList @"
    -NoExit
    -Command
    `$env:LOG_LEVEL='DEBUG';
    `$env:FILE_LOGGING='true';
    `$env:FLASK_ENV='development';
    Write-Host '========================================';
    Write-Host 'FRONTEND SERVER - Port 5000';
    Write-Host '========================================';
    Write-Host '';
    cd frontend;
    python app.py
"@

Write-Host "[OK] Frontend starting in new window..."
Write-Host ""

Write-Host "=" * 70
Write-Host "Servers Started!"
Write-Host "=" * 70
Write-Host ""
Write-Host "Access the application:"
Write-Host "  Frontend: http://localhost:5000"
Write-Host "  Backend:  http://localhost:8000"
Write-Host "  API Docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "Logs are displayed in separate terminal windows"
Write-Host "Log files are saved to: ./logs/"
Write-Host ""
Write-Host "To stop servers:"
Write-Host "  Close the terminal windows or press Ctrl+C in each"
Write-Host ""
Write-Host "Press any key to exit this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Made with Bob
