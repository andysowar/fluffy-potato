import os
from typing import Dict, Iterable, Optional

import requests

from kym_scraper import fetch_details as scrape_details
from memedict import search as scrape_search

try:  # Prefer the actively maintained culturgen library when available
    import culturgen  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    culturgen = None


COMMUNITY_API_BASE_URL = os.getenv("COMMUNITY_API_BASE_URL", "").rstrip("/")
REQUEST_TIMEOUT = 10


def _first_present(data: Dict, keys: Iterable[str]) -> str:
    for key in keys:
        value = data.get(key)
        if value:
            return str(value)
    return ""


def _as_dict(data) -> Optional[Dict]:
    """Coerce common culturgen objects into dictionaries."""

    if not data:
        return None

    if isinstance(data, dict):
        return data

    if hasattr(data, "__dict__"):
        return dict(data.__dict__)

    return None


def _normalize_entry(raw, fallback_title: Optional[str] = None) -> Optional[Dict[str, str]]:
    """Normalize various entry shapes into a consistent dictionary."""

    # Handle list/tuple responses by returning the first successful normalization
    if isinstance(raw, (list, tuple)):
        for candidate in raw:
            normalized = _normalize_entry(candidate)
            if normalized:
                return normalized
        return None

    raw = _as_dict(raw)

    if not raw:
        return None

    # culturgen may return nested "sections"; prefer explicit keys first
    sections = raw.get("sections")
    section_lookup = {}
    if isinstance(sections, dict):
        section_lookup = {str(k).strip().lower(): v for k, v in sections.items()}
    elif isinstance(sections, list):
        for section in sections:
            if isinstance(section, dict) and section.get("title"):
                section_lookup[section["title"].strip().lower()] = section.get("body") or section.get(
                    "content"
                )

    def section_text(*names: str) -> str:
        for name in names:
            if section_lookup.get(name.lower()):
                return str(section_lookup[name.lower()])
        return ""

    def clean(value: str) -> str:
        return value.strip() if isinstance(value, str) else str(value).strip() if value is not None else ""

    normalized = {
        "title": clean(_first_present(raw, ["title", "name", "slug"])) or None,
        "origin": clean(_first_present(raw, ["origin", "about", "description", "summary"]))
        or clean(section_text("origin")),
        "spread": clean(_first_present(raw, ["spread", "overview"])) or clean(section_text("spread")),
        "analysis": clean(_first_present(raw, ["analysis", "notes"])) or clean(section_text("analysis")),
    }

    # Require at least a title to consider the entry valid
    if not normalized["title"] and fallback_title:
        normalized["title"] = fallback_title

    if not normalized["title"]:
        return None

    return normalized


def fetch_from_community_api(slug: str) -> Optional[Dict[str, str]]:
    if not COMMUNITY_API_BASE_URL:
        return None

    try:
        response = requests.get(
            f"{COMMUNITY_API_BASE_URL}/memes/{slug}", timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError):
        return None

    return _normalize_entry(payload, fallback_title=slug)


def fetch_with_culturgen(slug: str) -> Optional[Dict[str, str]]:
    if not culturgen:
        return None

    def try_fetch(target: str) -> Optional[Dict[str, str]]:
        try:
            result = culturgen.fetch(target)  # type: ignore[attr-defined]
        except Exception:
            return None

        return _normalize_entry(result, fallback_title=slug)

    # Try direct slug, a spaced variant, and the full KYM URL before search
    for candidate in {
        slug,
        slug.replace("-", " "),
        f"https://knowyourmeme.com/memes/{slug}",
    }:
        normalized = try_fetch(candidate)
        if normalized:
            return normalized

    # If a direct fetch failed, try to resolve via search results (best effort)
    try:
        search_results = culturgen.search(slug)  # type: ignore[attr-defined]
    except Exception:
        return None

    if isinstance(search_results, dict):
        search_results = [search_results]

    if not isinstance(search_results, (list, tuple)):
        return None

    for candidate in search_results:
        candidate_dict = _as_dict(candidate)
        if not candidate_dict:
            continue

        candidate_slug = _first_present(candidate_dict, ["slug", "name", "title"]).replace(" ", "-")
        candidate_url = _first_present(candidate_dict, ["url", "link", "permalink", "href"])

        normalized = try_fetch(candidate_url or candidate_slug)
        if normalized:
            return normalized

    return None


def fetch_meme_entry(slug: str) -> Optional[Dict[str, str]]:
    entry = fetch_from_community_api(slug)

    if entry:
        return entry

    entry = fetch_with_culturgen(slug)
    if entry:
        return entry

    return _normalize_entry(scrape_search(slug), fallback_title=slug)


def fetch_meme_details(slug: str) -> Optional[Dict[str, object]]:
    """Return structured meme details scraped directly from KnowYourMeme."""

    try:
        return scrape_details(slug)
    except Exception:
        return None
