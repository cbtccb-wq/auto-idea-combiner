from __future__ import annotations

from html import unescape
from urllib.parse import quote
from typing import Any

import feedparser
import httpx


USER_AGENT = "AutoIdeaCombiner/0.1"


async def _fetch_json(url: str, headers: dict[str, str] | None = None) -> Any:
    async with httpx.AsyncClient(timeout=10.0, headers=headers or {"User-Agent": USER_AGENT}) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


def fetch_wikipedia_summary(query: str) -> str:
    if not query.strip():
        return ""

    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(query.strip(), safe='')}"
    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": USER_AGENT}) as client:
            response = client.get(url)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError:
        return ""

    return str(payload.get("extract") or "")


def fetch_github_trending(language: str = "", since: str = "daily") -> list[dict]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/atom+xml"}
    query_language = language.strip()
    time_window = since.strip().lower() or "daily"

    if query_language:
        feed_url = (
            "https://github.com/trending/"
            f"{query_language}?since={time_window}&spoken_language_code=en"
        )
    else:
        feed_url = f"https://github.com/trending?since={time_window}&spoken_language_code=en"

    try:
        with httpx.Client(timeout=10.0, follow_redirects=True, headers=headers) as client:
            response = client.get(feed_url)
            response.raise_for_status()
            html_body = response.text
    except httpx.HTTPError:
        return []

    entries: list[dict] = []
    for line in html_body.splitlines():
        if "/stargazers" not in line or "href=" not in line:
            continue
        if len(entries) >= 10:
            break
        href = line.split('href="', 1)[1].split('"', 1)[0]
        if href.count("/") < 2:
            continue
        repository = href.strip("/").split("/stargazers", 1)[0]
        if "/" not in repository:
            continue
        entries.append(
            {
                "repository": repository,
                "url": f"https://github.com/{repository}",
                "language": query_language or None,
                "since": time_window,
            }
        )

    if entries:
        unique_entries: list[dict] = []
        seen: set[str] = set()
        for entry in entries:
            repo = entry["repository"]
            if repo in seen:
                continue
            seen.add(repo)
            unique_entries.append(entry)
        return unique_entries

    rss_url = "https://github.com/topics/trending.atom"
    parsed = feedparser.parse(rss_url)
    return [
        {
            "repository": unescape(entry.get("title", "")),
            "url": entry.get("link", ""),
            "language": query_language or None,
            "since": time_window,
        }
        for entry in parsed.entries[:10]
        if entry.get("title")
    ]


def fetch_news_headlines(api_key: str, query: str = "technology") -> list[str]:
    if not api_key:
        return []

    params = {
        "apiKey": api_key,
        "q": query,
        "language": "en",
        "pageSize": 10,
        "sortBy": "publishedAt",
    }

    try:
        with httpx.Client(timeout=10.0, headers={"User-Agent": USER_AGENT}) as client:
            response = client.get("https://newsapi.org/v2/everything", params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError:
        return []

    headlines: list[str] = []
    for article in payload.get("articles", []):
        title = str(article.get("title") or "").strip()
        if title:
            headlines.append(title)
    return headlines
