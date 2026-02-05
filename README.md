# ExoTerra Resource System Controller Script Guide

## Script Documentation
Is located under `/docs/testscripts_customer.md`

## Running the installer
```
# Tested on Ubuntu 22.04 with Python 3.10.12
chmod +x ./install.sh
sudo ./install.sh
```
This installs everything into a virtualenv .venv folder. Make sure to source this folder before running scripts:
```
source .venv/bin/activate
```

This script will attempt to install the required python packages and then add the user to the dialout group for serial communication.

## Running the example.py
The example.py script is located under `scripts/example.py` and demonstrates the step-by-step process for operating the thruster from initialization to steady state.