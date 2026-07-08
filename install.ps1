# Windows installer for ExoTerra Resource System Controller Script
# Requires: Python 3.10+ installed and available on PATH
# Run from the repo root in PowerShell (no elevation required):
#   .\install.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Verify Python is available
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python was not found on PATH. Install Python 3.10+ from https://www.python.org/downloads/ and ensure 'Add Python to PATH' is checked."
    exit 1
}

$pyVersion = python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "Found Python $pyVersion"

# Create and activate virtual environment
Write-Host "Creating virtual environment (.venv)..."
python -m venv .venv

$activateScript = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (-not (Test-Path $activateScript)) {
    Write-Error "Virtual environment creation failed; Activate.ps1 not found."
    exit 1
}

. $activateScript

# Install Python dependencies
Write-Host "Installing Python packages from requirements.txt..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# wxPython ships as a wheel on PyPI for Windows — no extras URL needed
Write-Host "Installing wxPython..."
python -m pip install wxPython==4.2.5

Write-Host ""
Write-Host "Installation complete!"
Write-Host ""
Write-Host "Serial ports on Windows are listed as COM ports (e.g., COM3, COM4)."
Write-Host "No additional group membership is required on Windows."
Write-Host ""
Write-Host "To activate the virtual environment in future sessions, run:"
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "If script execution is blocked, run once as an administrator:"
Write-Host "    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned"
