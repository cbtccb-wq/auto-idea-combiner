from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md"}


def _read_text_file(path: Path) -> str | None:
    for encoding in ("utf-8", "utf-8-sig", "cp932", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None
    return None


def scan_directory(path: str) -> list[str]:
    base_path = Path(path).expanduser()
    if not base_path.exists() or not base_path.is_dir():
        return []

    contents: list[str] = []
    for file_path in base_path.rglob("*"):
        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS or not file_path.is_file():
            continue
        content = _read_text_file(file_path)
        if content:
            contents.append(content)
    return contents


def get_recent_files(dirs: list[str], max_files: int = 50) -> list[dict]:
    candidates: list[dict] = []

    for directory in dirs:
        base_path = Path(directory).expanduser()
        if not base_path.exists() or not base_path.is_dir():
            continue

        for file_path in base_path.rglob("*"):
            if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS or not file_path.is_file():
                continue
            content = _read_text_file(file_path)
            if not content:
                continue
            try:
                modified_at = datetime.fromtimestamp(
                    file_path.stat().st_mtime,
                    tz=timezone.utc,
                )
            except OSError:
                continue
            candidates.append(
                {
                    "path": str(file_path),
                    "content": content,
                    "modified_at": modified_at,
                }
            )

    candidates.sort(key=lambda item: item["modified_at"], reverse=True)
    return candidates[:max_files]
