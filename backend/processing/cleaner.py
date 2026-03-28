from __future__ import annotations

import html
import re


HTML_TAG_RE = re.compile(r"<[^>]+>")
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
WHITESPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    cleaned = html.unescape(text or "")
    cleaned = HTML_TAG_RE.sub(" ", cleaned)
    cleaned = CONTROL_CHARS_RE.sub(" ", cleaned)
    cleaned = WHITESPACE_RE.sub(" ", cleaned)
    return cleaned.strip()
