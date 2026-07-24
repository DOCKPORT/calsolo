#!/bin/bash

# Navigate to the script directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Check if python3 is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 could not be found. Please install it."
    exit
fi

# Run the application
/home/dockport/DOCK-HQ/DEV/venv/bin/python3 calsolo.py
