from __future__ import annotations

import platform
import subprocess


def _run_command(command: list[str]) -> str | None:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            check=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.SubprocessError):
        return None

    value = completed.stdout.strip()
    return value or None


def get_clipboard_text() -> str | None:
    system = platform.system().lower()

    if system == "windows":
        return _run_command(["powershell", "-NoProfile", "-Command", "Get-Clipboard -Raw"])
    if system == "darwin":
        return _run_command(["pbpaste"])

    for candidate in (["wl-paste", "-n"], ["xclip", "-selection", "clipboard", "-o"], ["xsel", "--clipboard", "--output"]):
        text = _run_command(candidate)
        if text:
            return text
    return None
