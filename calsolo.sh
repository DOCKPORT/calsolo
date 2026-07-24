#!/bin/bash

# Navigate to the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install it."
    exit 1
fi

# Determine Python interpreter
# Prefer a venv in DEV/ relative to DOCK-HQ; fall back to system python3
PYTHON=""
_venv="$DIR/../../venv/bin/python3"
if [ -f "$_venv" ]; then
    PYTHON="$_venv"
elif command -v python3 &> /dev/null; then
    PYTHON="$(command -v python3)"
else
    echo "No Python interpreter found."
    exit 1
fi

# Run the application (desktop entry installation is handled by calsolo.py)
"$PYTHON" calsolo.py