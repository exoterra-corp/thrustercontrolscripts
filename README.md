# ExoTerra Resource System Controller Script Guide

## Script Documentation
Full documentation is located in [docs/testscripts_customer.md](docs/testscripts_customer.md).

## Running the installer

### Linux (Ubuntu 22.04)
```bash
# Tested on Ubuntu 22.04 with Python 3.10.12
chmod +x ./install.sh
sudo ./install.sh
```
This installs everything into a virtualenv `.venv` folder. Activate it before running scripts:
```bash
source .venv/bin/activate
```
The script installs the required Python packages and adds the current user to the `dialout` group for serial communication.

### Windows
Requires [Python 3.10+](https://www.python.org/downloads/) installed with **"Add Python to PATH"** checked.

Open PowerShell in the repo root and run:
```powershell
.\install.ps1
```
If script execution is blocked, first run (once, as Administrator):
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
This installs everything into a `.venv` folder. Activate it before running scripts:
```powershell
.\.venv\Scripts\Activate.ps1
```
Serial ports on Windows are addressed as COM ports (e.g., `COM3`). No additional group membership is required.

## Running the example.py
The example.py script is located under `scripts/example.py` and demonstrates the step-by-step process for operating the thruster from initialization to steady state.