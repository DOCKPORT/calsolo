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

# ---------------------------------------------------------------------------
# Desktop integration — install launcher + icon (one-time)
# ---------------------------------------------------------------------------
DESKTOP_FILE="$HOME/.local/share/applications/Calsolo.desktop"
ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"
SCRIPT_PATH="$(readlink -f "$0")"

if [ ! -f "$DESKTOP_FILE" ]; then
    echo "Installing desktop entry..."
    mkdir -p "$ICON_DIR"
    cp calsolo.svg "$ICON_DIR/"
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0.0
Name=Calsolo
Comment=Terminal Calculator
Exec=$SCRIPT_PATH
Path=$DIR
Icon=calsolo
Type=Application
Categories=Finance;Utility;
Terminal=false
StartupNotify=false
EOF
    # Refresh desktop database if available
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$HOME/.local/share/applications/" 2>/dev/null || true
    fi
    echo "Desktop entry installed. You can now launch Calsolo from your app menu."
fi

# ---------------------------------------------------------------------------
# Determine Python interpreter
# Prefer a venv in DEV/ relative to DOCK-HQ; fall back to system python3
# ---------------------------------------------------------------------------
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

# Run the application
"$PYTHON" calsolo.py