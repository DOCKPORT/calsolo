import math
import re
import sys
from asteval import Interpreter
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPlainTextEdit, QLineEdit, QPushButton, QApplication,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QScreen

from version import VERSION
from icon import get_app_icon
from colors import (
    BG,
    OUTPUT_BG,
    DIALOG_BORDER,
    LABEL_TEXT,
    OUTPUT_TEXT, OUTPUT_BORDER,
    INPUT_TEXT, INPUT_BORDER,
    BUTTON_TEXT, BUTTON_BORDER, BUTTON_HOVER_TEXT,
    SCROLLBAR_HANDLE, SCROLLBAR_HANDLE_HOVER,
)


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


BUILTIN_VARS = {
    'sqrt': math.sqrt, 'abs': abs, 'round': round,
    'pi': math.pi, 'e': math.e, 'pow': pow,
    'sin': math.sin, 'cos': math.cos, 'tan': math.tan,
}


class CalculatorWindow(QDialog):
    """
    A standalone window for the Terminal Calculator.
    Uses asteval for safe math expression evaluation.
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

        # Safe math interpreter
        self.interp = Interpreter(usersyms=BUILTIN_VARS.copy())

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
        self.interp = Interpreter(usersyms=BUILTIN_VARS.copy())

    def _format_result(self, val: float | int) -> str:
        """Format a numeric result nicely."""
        if isinstance(val, float):
            return f"{val:g}"
        return str(val)

    def _on_calc_enter(self):
        text = self.calc_input.text().strip()
        if not text:
            return

        self.calc_history.appendPlainText(f"> {text}")

        # Special vars command
        if text.lower() == 'vars':
            user_vars = {
                k: v for k, v in self.interp.symtable.items()
                if not callable(v) and k != '__builtins__'
            }
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
            # but leave "10 % 3" (modulo) alone
            # Only match percent at end of a number
            if '%' in text:
                processed = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1)/100', text)
            else:
                processed = text

            result = self.interp(processed)

            # asteval returns None for assignment statements
            if result is None:
                # Check if this was an assignment by looking for '='
                if '=' in text:
                    var_name = text.split('=', 1)[0].strip()
                    if var_name in self.interp.symtable:
                        val = self.interp.symtable[var_name]
                        self.calc_history.appendPlainText(
                            f"  {var_name} = {self._format_result(val)}"
                        )
            else:
                self.calc_history.appendPlainText(f"  = {self._format_result(result)}")

        except Exception as e:
            msg = str(e)
            # Clean up asteval's verbose error messages
            if msg.startswith("NameError: name '") and msg.endswith("' is not defined"):
                
                pass
            self.calc_history.appendPlainText(f"  Error: {msg}")

        self.calc_input.clear()
        self.calc_input.setFocus()

    def showEvent(self, event):
        super().showEvent(event)
        self.calc_input.setFocus()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = CalculatorWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()