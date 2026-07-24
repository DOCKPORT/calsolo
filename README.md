# Calsolo

A standalone terminal-style calculator with a dark theme, powered by a **Rust** calculation engine (`calc_engine`) via PyO3.

## Features

- Safe expression evaluation using a Rust backend — no system calls, no file I/O, pure math only
- Variable assignment and recall — `x = 42`, then `x * 2`
- `vars` command lists all user-defined variables
- Percentage shorthand — `50%` evaluates to `0.5`
- History panel with **Clear** button or `Ctrl+L` shortcut
- Dark terminal-inspired theme
- Scale-factor support for high-DPI displays

## Dependencies

- Python 3.10+
- PySide6
- Rust calc engine (built with maturin + PyO3)

## License

MIT