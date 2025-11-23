"""Lightweight KnowYourMeme scraper for structured meme details."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup, Tag

DEFAULT_TIMEOUT = 10
BASE_URL = "https://knowyourmeme.com/memes"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    )
}


def _text_or_empty(node: Optional[Tag]) -> str:
    return node.get_text(strip=True) if node else ""


def _extract_sections(soup: BeautifulSoup) -> List[Dict[str, str]]:
    sections: List[Dict[str, str]] = []
    for header in soup.select("article.entry h2[id]"):
        title = _text_or_empty(header)
        if not title:
            continue

        body_parts: List[str] = []
        for sibling in header.find_all_next():
            if sibling.name == "h2":
                break
            if isinstance(sibling, Tag):
                text = sibling.get_text("\n", strip=True)
                if text:
                    body_parts.append(text)
        sections.append({"title": title, "body": "\n\n".join(body_parts)})
    return sections


def _parse_stat_table(soup: BeautifulSoup) -> Dict[str, str]:
    stats: Dict[str, str] = {}
    for row in soup.select("section.info dl"):
        children = [child for child in row.children if isinstance(child, Tag)]
        for name, value in zip(children[0::2], children[1::2]):
            key = _text_or_empty(name).rstrip(":")
            if key:
                stats[key.lower()] = _text_or_empty(value)
    return stats


def _parse_tags(soup: BeautifulSoup) -> List[str]:
    return [link.get_text(strip=True) for link in soup.select("a.tag") if link.get_text(strip=True)]


def _parse_views(text: str) -> Optional[int]:
    match = re.search(r"([\d,]+)", text)
    if not match:
        return None
    try:
        return int(match.group(1).replace(",", ""))
    except ValueError:
        return None


def fetch_details(slug: str) -> Dict[str, object]:
    response = requests.get(f"{BASE_URL}/{slug}", headers=HEADERS, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    title = (
        soup.find("meta", {"property": "og:title"}).get("content")
        if soup.find("meta", {"property": "og:title"})
        else _text_or_empty(soup.find("h1"))
    )
    image_url = (
        soup.find("meta", {"property": "og:image"}).get("content")
        if soup.find("meta", {"property": "og:image"})
        else None
    )
    image_alt = None
    if image_url:
        image_alt = _text_or_empty(soup.find("figure", {"class": "photo"})) or title

    stats = _parse_stat_table(soup)

    sections = _extract_sections(soup)

    return {
        "title": title,
        "link": f"{BASE_URL}/{slug}",
        "image": {"url": image_url, "alt": image_alt},
        "views": _parse_views(stats.get("views", "")),
        "sections": sections,
        "type": [stats.get("type", "")] if stats.get("type") else [],
        "year": stats.get("year", ""),
        "origin": stats.get("origin", ""),
        "region": stats.get("region", ""),
        "tags": _parse_tags(soup),
    }
