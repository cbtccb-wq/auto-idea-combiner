from backend.collectors.clipboard import get_clipboard_text
from backend.collectors.external_api import (
    fetch_github_trending,
    fetch_news_headlines,
    fetch_wikipedia_summary,
)
from backend.collectors.local_files import get_recent_files, scan_directory

__all__ = [
    "fetch_github_trending",
    "fetch_news_headlines",
    "fetch_wikipedia_summary",
    "get_clipboard_text",
    "get_recent_files",
    "scan_directory",
]
