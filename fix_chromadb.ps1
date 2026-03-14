# Fix ChromaDB Corruption Issue
# This script will reset the ChromaDB database

Write-Host "=" * 70
Write-Host "Fixing ChromaDB Corruption Issue"
Write-Host "=" * 70
Write-Host ""

# Stop any running Python processes
Write-Host "Step 1: Stopping any running backend processes..."
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Write-Host "✓ Processes stopped"
Write-Host ""

# Backup and remove ChromaDB directory
Write-Host "Step 2: Removing corrupted ChromaDB directory..."
if (Test-Path ".chromadb") {
    if (Test-Path ".chromadb_backup") {
        Remove-Item ".chromadb_backup" -Recurse -Force
    }
    Rename-Item ".chromadb" ".chromadb_backup"
    Write-Host "✓ Old ChromaDB backed up to .chromadb_backup"
} else {
    Write-Host "✓ No existing ChromaDB directory found"
}
Write-Host ""

# Clear log files
Write-Host "Step 3: Clearing old log files..."
Get-ChildItem logs\*.log | ForEach-Object {
    Clear-Content $_.FullName
}
Write-Host "✓ Log files cleared"
Write-Host ""

Write-Host "=" * 70
Write-Host "ChromaDB Reset Complete!"
Write-Host "=" * 70
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Start the backend:"
Write-Host "   python -m uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000"
Write-Host ""
Write-Host "2. The backend will automatically recreate ChromaDB with fresh data"
Write-Host ""
Write-Host "3. Upload a file and watch for multi-agent logs!"
Write-Host ""

# Made with Bob
