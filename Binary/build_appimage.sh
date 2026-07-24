#!/bin/bash
set -e

echo "================================"
echo " Running PyInstaller..."
echo "================================"
cd /build/Binary
pyinstaller --noconfirm Calsolo.spec

echo "================================"
echo " Building AppImage..."
echo "================================"
APPDIR=Calsolo.AppDir
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
cp dist/Calsolo "$APPDIR/usr/bin/Calsolo"

# Create the AppRun wrapper script — suppresses host GTK/GVFS/library conflicts
cat > "$APPDIR/AppRun" << 'APPRUNEOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "$0")")"
export GIO_EXTRA_MODULES=""
export GIO_MODULE_DIR=/nonexistent
export GTK_MODULES=""
export GTK_PATH=""
export NO_AT_BRIDGE=1
# Suppress harmless GTK module loading failures (e.g. xapp-gtk3-module missing)
exec 2> >(grep -v 'Failed to load module' >&2)
exec "${HERE}/usr/bin/Calsolo"
APPRUNEOF
chmod +x "$APPDIR/AppRun"

# Copy the app icon and create the required .desktop file for appimagetool
cp /build/calsolo.svg "$APPDIR/"
cat > "$APPDIR/Calsolo.desktop" << DESKEOF
[Desktop Entry]
Name=Calsolo
Comment=Terminal Calculator
Exec=Calsolo
Icon=calsolo
Type=Application
Categories=Finance;Utility;
Terminal=false
DESKEOF

if [ ! -f /build/Binary/appimagetool ]; then
    echo "Downloading appimagetool..."
    wget -q https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage -O /build/Binary/appimagetool
    chmod +x /build/Binary/appimagetool
fi

ARCH=x86_64 /build/Binary/appimagetool --appimage-extract-and-run "$APPDIR"

# appimagetool names the output after the .desktop entry name
# Calsolo.desktop → Calsolo-x86_64.AppImage — which is already correct
echo "Output: Calsolo-x86_64.AppImage"
cp -v Calsolo-x86_64.AppImage /build/ 2>/dev/null || \
    echo "[!] Warning: Could not copy AppImage to /build/"
