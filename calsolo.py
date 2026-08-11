import importlib.util
import os
import re
import sys


def _load_calc_engine():
    """Import CalcEngine, preferring pip-installed, falling back to local build."""
    try:
        from _calc_rs import CalcEngine
        return CalcEngine
    except ModuleNotFoundError:
        so_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "calc_engine", "target", "release", "lib_calc_rs.so",
        )
        if not os.path.exists(so_path):
            raise
        spec = importlib.util.spec_from_file_location("_calc_rs", so_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod.CalcEngine


CalcEngine = _load_calc_engine()

from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from colors import (
    BG,
    BUTTON_BORDER,
    BUTTON_HOVER_TEXT,
    BUTTON_TEXT,
    DIALOG_BORDER,
    INPUT_BORDER,
    INPUT_TEXT,
    LABEL_TEXT,
    OUTPUT_BG,
    OUTPUT_BORDER,
    OUTPUT_TEXT,
    SCROLLBAR_HANDLE,
    SCROLLBAR_HANDLE_HOVER,
)
from icon import SVG_LOGO, get_app_icon
from version import VERSION

STYLESHEET_TEMPLATE = """
    QDialog {{
        background-color: {bg};
        border: {border}px solid {dialog_border};
        border-radius: {radius}px;
    }}
    QLabel {{
        color: {label_text};
        font-family: 'Fira Code', 'DejaVu Sans Mono', 'Ubuntu Mono', monospace;
        font-size: {label_font}px;
        font-weight: bold;
        border: none;
    }}
    QPlainTextEdit {{
        background-color: {output_bg};
        color: {output_text};
        border: 1px solid {output_border};
        border-radius: {rounding}px;
        font-family: 'Fira Code', 'Courier New', 'DejaVu Sans Mono', monospace;
        font-size: {output_font}px;
        padding: {pad}px;
    }}
    QScrollBar:vertical {{
        border: none;
        background: {bg};
        width: {scroll_w}px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {scrollbar_handle};
        min-height: {scroll_h}px;
        border-radius: {scroll_r}px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {scrollbar_handle_hover};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: none;
    }}
    QLineEdit {{
        background-color: {bg};
        color: {input_text};
        border: 1px solid {input_border};
        border-radius: {edit_r}px;
        font-family: 'Fira Code', 'DejaVu Sans Mono', 'Ubuntu Mono', monospace;
        font-size: {edit_font}px;
        padding: {edit_pad}px;
    }}
    QPushButton {{
        background-color: {bg};
        color: {button_text};
        border: 1px solid {button_border};
        border-radius: {btn_r}px;
        font-family: 'Fira Code', 'Courier New', 'DejaVu Sans Mono', monospace;
        font-weight: bold;
        padding: {btn_pad_v}px {btn_pad_h}px;
    }}
    QPushButton:hover {{
        color: {button_hover_text};
    }}
"""


class CalculatorWindow(QDialog):
    """
    A standalone window for the Terminal Calculator.
    Uses the Rust calc_engine for safe math expression evaluation.
    """
    def __init__(self, parent=None, scale_factor=None):
        """Standalone Terminal Calculator Window."""
        super().__init__(parent)
        if scale_factor is None:
            screen = QApplication.primaryScreen()
            if screen is not None:
                size = screen.size()
                scale_factor = min(size.width() / 1920, size.height() / 1080)
                scale_factor = max(0.8, scale_factor)
            else:
                scale_factor = 1.0
        self.scale_factor = scale_factor
        self.s = lambda val: int(val * self.scale_factor)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setWindowTitle(f"Calsolo {VERSION}")
        self.setWindowIcon(get_app_icon())
        self.setMinimumSize(self.s(500), self.s(600))

        self._apply_stylesheet()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # History
        self.calc_history = QPlainTextEdit()
        self.calc_history.setReadOnly(True)
        self.layout.addWidget(self.calc_history)

        # Input Row
        input_container = QWidget()
        input_container.setStyleSheet("background: transparent; border: none;")
        input_row = QHBoxLayout(input_container)
        input_row.setContentsMargins(0, 0, 0, 0)

        self.prompt = QLabel("> ")
        self.calc_input = QLineEdit()
        self.calc_input.setPlaceholderText("")
        self.calc_input.returnPressed.connect(self._on_calc_enter)

        self.clear_btn = QPushButton("CLEAR")
        self.clear_btn.setAutoDefault(False)
        self.clear_btn.setDefault(False)
        self.clear_btn.clicked.connect(self._clear_history)

        input_row.addWidget(self.prompt)
        input_row.addWidget(self.calc_input)
        input_row.addWidget(self.clear_btn)
        self.layout.addWidget(input_container)

        # Ctrl+L shortcut for Clear
        QShortcut(Qt.Key.Key_L | Qt.Modifier.CTRL, self, self._clear_history)

        # Rust calc engine
        self.engine = CalcEngine()

    def _apply_stylesheet(self):
        s = self.s
        self.setStyleSheet(STYLESHEET_TEMPLATE.format(
            # Colors
            bg=BG,
            output_bg=OUTPUT_BG,
            dialog_border=DIALOG_BORDER,
            label_text=LABEL_TEXT,
            output_text=OUTPUT_TEXT,
            output_border=OUTPUT_BORDER,
            input_text=INPUT_TEXT,
            input_border=INPUT_BORDER,
            button_text=BUTTON_TEXT,
            button_border=BUTTON_BORDER,
            button_hover_text=BUTTON_HOVER_TEXT,
            scrollbar_handle=SCROLLBAR_HANDLE,
            scrollbar_handle_hover=SCROLLBAR_HANDLE_HOVER,
            # Sizing
            border=s(2), radius=s(12),
            label_font=s(20),
            output_font=s(18), pad=s(10),
            rounding=s(6),
            scroll_w=s(6), scroll_h=s(20), scroll_r=s(3),
            edit_font=s(20), edit_pad=s(8), edit_r=s(4),
            btn_r=s(4), btn_pad_v=s(8), btn_pad_h=s(15),
        ))

    def _clear_history(self):
        self.calc_history.clear()
        self.engine.clear_vars()

    def _format_result(self, val: float) -> str:
        """Format a numeric result nicely — no scientific notation."""
        if isinstance(val, float):
            # Whole number → show as integer
            if val == int(val):
                return str(int(val))
            # Otherwise show up to 10 decimal places, strip trailing zeros
            s = f"{val:.10f}".rstrip("0").rstrip(".")
            return s
        return str(val)

    def _on_calc_enter(self):
        text = self.calc_input.text().strip()
        if not text:
            return

        self.calc_history.appendPlainText(f"> {text}")

        # Special vars command
        if text.lower() == 'vars':
            user_vars = self.engine.get_all_vars()
            if user_vars:
                for k, v in user_vars.items():
                    self.calc_history.appendPlainText(f"  {k} = {self._format_result(v)}")
            else:
                self.calc_history.appendPlainText("  (No variables)")
            self.calc_input.clear()
            self.calc_input.setFocus()
            return

        try:
            # Handle percentage: convert standalone "50%" → "50/100"
            if '%' in text:
                processed = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1)/100', text)
            else:
                processed = text

            result = self.engine.eval(processed)

            # The Rust engine returns the value for assignments too —
            # no need for the None check like asteval
            self.calc_history.appendPlainText(f"  = {self._format_result(result)}")

        except Exception as e:  # noqa: BLE001 — intentionally catch all errors to display in GUI
            msg = str(e)
            self.calc_history.appendPlainText(f"  Error: {msg}")

        self.calc_input.clear()
        self.calc_input.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.calc_input.setFocus()


# ---------------------------------------------------------------------------
# Desktop entry installation (runs once on first launch)
# ---------------------------------------------------------------------------

def _install_desktop_entry() -> None:
    """Create a .desktop file and icon for the system launcher.

    Detects whether the app is running from an AppImage or from source,
    then installs the appropriate launcher at
    ``~/.local/share/applications/Calsolo.desktop``.
    Only runs if the file does not already exist.
    """
    import subprocess

    desktop_path = os.path.expanduser(
        "~/.local/share/applications/Calsolo.desktop",
    )
    if os.path.exists(desktop_path):
        return

    # Store the icon directly in ~/.local/share/icons (no hicolor theme folders).
    icon_dir = os.path.expanduser("~/.local/share/icons")
    icon_dst = os.path.join(icon_dir, "calsolo.svg")
    icon_path = icon_dst
    os.makedirs(icon_dir, exist_ok=True)

    # Determine the binary path and build the Exec line.
    appimage = os.environ.get("APPIMAGE")
    if appimage:
        exec_line = appimage
    else:
        # Running from source
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exec_line = f"{sys.executable} {os.path.join(script_dir, 'calsolo.py')}"

    # Write the icon from the embedded SVG logo.
    # Avoids depending on a packaged .svg file, which is never bundled
    # into the AppImage bundle.
    try:
        with open(icon_dst, "w") as f:
            f.write(SVG_LOGO)
    except Exception as e:  # noqa: BLE001 — non-critical, warn instead of fail
        print(f"Warning: could not write icon to {icon_dst}: {e}")

    # Write the .desktop file, referencing the icon by absolute path
    # so the launcher finds it without a theme lookup.
    os.makedirs(os.path.dirname(desktop_path), exist_ok=True)
    with open(desktop_path, "w") as f:
        f.write(f"""[Desktop Entry]
Version={VERSION}
Name=Calsolo
Comment=Terminal Calculator
Exec={exec_line}
Path={os.path.dirname(os.path.abspath(__file__))}
Icon={icon_path}
Type=Application
Categories=Finance;Utility;
Terminal=false
StartupNotify=false
""")

    # Refresh the desktop database
    try:
        subprocess.run(
            ["update-desktop-database", os.path.dirname(desktop_path)],
            capture_output=True,
            check=False,
        )
    except Exception:  # noqa: BLE001, S110 — non-critical, skip desktop db refresh if fails
        pass


def main():
    _install_desktop_entry()
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = CalculatorWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()