"""Online film search via a TMDB-compatible API, plus an IMDb scrape skeleton for Exercise 13.

Providers:
    tmdb   free for non-commercial apps (no ads / purchases), needs TMDB attribution
    amodb  paid, allows commercial use, same endpoints and JSON as TMDB v3

Pick the provider with FILM_API_PROVIDER (or the app's Online screen) and supply a key via
FILM_API_KEY, or the provider-specific TMDB_API_KEY / AMODB_KEY.
"""

from __future__ import annotations

import os
from typing import Any

import requests

PROVIDERS = {
    "tmdb": {
        "name": "TMDB",
        "base_url": "https://api.themoviedb.org/3",
        "key_env": "TMDB_API_KEY",
    },
    "amodb": {
        "name": "amodb",
        "base_url": "https://api.amodb.dev/3",
        "key_env": "AMODB_KEY",
    },
}
DEFAULT_PROVIDER = "tmdb"
DEFAULT_TIMEOUT = 10

# Kept for older imports; the active base URL now comes from the provider.
TMDB_BASE = PROVIDERS["tmdb"]["base_url"]


class FilmSearchError(Exception):
    """Raised when an online search fails."""


def get_provider(provider: str | None = None) -> str:
    """Return a known provider id from the argument or FILM_API_PROVIDER env var."""
    chosen = (provider or os.environ.get("FILM_API_PROVIDER") or DEFAULT_PROVIDER).strip().lower()
    if chosen not in PROVIDERS:
        raise FilmSearchError(
            f"Unknown provider '{chosen}'. Choose one of: {', '.join(PROVIDERS)}."
        )
    return chosen


def get_api_key(api_key: str | None = None, provider: str | None = None) -> str:
    """Return an API key from the argument, FILM_API_KEY, or the provider's own env var."""
    provider = get_provider(provider)
    key_env = PROVIDERS[provider]["key_env"]
    key = (
        (api_key or "").strip()
        or os.environ.get("FILM_API_KEY", "").strip()
        or os.environ.get(key_env, "").strip()
    )
    if not key:
        raise FilmSearchError(
            f"Missing {PROVIDERS[provider]['name']} API key. Enter it on the Online "
            f"screen, or set {key_env} in your environment (see README.md)."
        )
    return key


def _get_json(path: str, params: dict, api_key: str | None, provider: str | None, action: str) -> dict:
    """GET a provider endpoint and return its JSON, raising FilmSearchError on failure."""
    provider = get_provider(provider)
    info = PROVIDERS[provider]
    url = f"{info['base_url']}{path}"
    params = {**params, "api_key": get_api_key(api_key, provider)}

    # Messages are built from status codes, never from the exception text: request
    # errors embed the full URL, which includes the api_key query parameter.
    try:
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
    except requests.Timeout as exc:
        raise FilmSearchError(f"{info['name']} {action} timed out. Check your connection.") from exc
    except requests.RequestException as exc:
        raise FilmSearchError(
            f"{info['name']} {action} failed: could not connect ({type(exc).__name__})."
        ) from exc

    if response.status_code == 401:
        raise FilmSearchError(f"{info['name']} rejected the API key. Check it and try again.")
    if response.status_code == 429:
        raise FilmSearchError(f"{info['name']} rate limit hit. Wait a minute and retry.")
    if response.status_code >= 400:
        raise FilmSearchError(f"{info['name']} {action} failed (HTTP {response.status_code}).")

    try:
        return response.json()
    except ValueError as exc:
        raise FilmSearchError(f"{info['name']} returned an unreadable response.") from exc


def check_api_key(api_key: str | None = None, provider: str | None = None) -> str:
    """Make one cheap authenticated call; return the provider name if the key works."""
    provider = get_provider(provider)
    _get_json("/configuration", {}, api_key, provider, "key check")
    return PROVIDERS[provider]["name"]


def search_tmdb(
    query: str,
    api_key: str | None = None,
    limit: int = 8,
    provider: str | None = None,
) -> list[dict]:
    """
    Search the configured TMDB-compatible provider for movies matching query.

    Returns a list of Decider-shaped movie dicts (duration/genre may be incomplete
    until fetch_tmdb_details is called).
    """
    query = (query or "").strip()
    if not query:
        raise FilmSearchError("Search query cannot be empty.")

    provider = get_provider(provider)
    params = {
        "query": query,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    }
    data = _get_json("/search/movie", params, api_key, provider, "search")

    results = data.get("results") or []
    return [normalize_tmdb_result(item, provider=provider) for item in results[:limit]]


def fetch_tmdb_details(movie_id: int, api_key: str | None = None, provider: str | None = None) -> dict:
    """Fetch full movie details (runtime, genres, etc.)."""
    return _get_json(
        f"/movie/{movie_id}", {"language": "en-US"}, api_key, provider, "details"
    )


def normalize_tmdb_result(
    item: dict[str, Any],
    details: dict[str, Any] | None = None,
    provider: str = "tmdb",
) -> dict:
    """Convert TMDB JSON into the Decider movie dict shape."""
    source = details or item

    release = source.get("release_date") or item.get("release_date") or ""
    year = int(release[:4]) if len(release) >= 4 and release[:4].isdigit() else 0

    genre = "Unknown"
    if details and details.get("genres"):
        genre = details["genres"][0]["name"]
    elif item.get("genre_ids"):
        # Search results only include genre IDs; leave Unknown until details load
        genre = "Unknown"

    duration = int(details.get("runtime") or 0) if details else 0
    rating = float(source.get("vote_average") or item.get("vote_average") or 0)
    title = source.get("title") or item.get("title") or "Untitled"
    tmdb_id = source.get("id") or item.get("id")

    return {
        "title": title,
        "genre": genre,
        "mood": [],  # Exercise 14: guess moods from genre/overview
        "duration": duration,
        "rating": round(rating, 1),
        "year": year,
        "source": provider,
        "tmdb_id": tmdb_id,
        "overview": (source.get("overview") or item.get("overview") or "").strip(),
    }


def enrich_with_details(movie: dict, api_key: str | None = None, provider: str | None = None) -> dict:
    """Fetch details for a search result and return an updated movie dict."""
    tmdb_id = movie.get("tmdb_id")
    if not tmdb_id:
        raise FilmSearchError("Movie is missing tmdb_id; cannot fetch details.")
    provider = get_provider(provider or movie.get("source"))
    details = fetch_tmdb_details(int(tmdb_id), api_key=api_key, provider=provider)
    return normalize_tmdb_result(movie, details=details, provider=provider)


def scrape_imdb_search(query: str) -> list[dict]:
    """
    Exercise 13 — scrape IMDb search results with requests + BeautifulSoup.

    Warning: IMDb HTML changes often and may block scrapers. Prefer TMDB for
    real use. This is for learning only.

    TODO:
    1. GET https://www.imdb.com/find/?q=<query>&s=tt
    2. Parse with BeautifulSoup
    3. Extract title / year from result rows
    4. Return Decider-shaped dicts with source="imdb"
    """
    # Keep imports available for the exercise without requiring them at runtime yet
    _ = query
    raise NotImplementedError(
        "Exercise 13: implement scrape_imdb_search() — see EXERCISES.md"
    )


def merge_movies(local: list[dict], remote: list[dict]) -> list[dict]:
    """
    Merge remote movies into local list, deduping by lowercase title + year.
    Existing local entries win when titles match.
    """
    seen = {
        (_title_key(m.get("title", "")), int(m.get("year") or 0))
        for m in local
    }
    merged = list(local)
    for movie in remote:
        key = (_title_key(movie.get("title", "")), int(movie.get("year") or 0))
        if key in seen:
            continue
        seen.add(key)
        merged.append(movie)
    return merged


def _title_key(title: str) -> str:
    return " ".join(title.lower().split())


if __name__ == "__main__":
    import sys

    # Quick key test: python film_search.py [title]
    try:
        provider_name = check_api_key()
        print(f"{provider_name} key works.")
        query = " ".join(sys.argv[1:]) or "Inception"
        for hit in search_tmdb(query, limit=3):
            print(f"  {hit['title']} ({hit['year']}) {hit['rating']}/10")
    except FilmSearchError as exc:
        print(exc)
        sys.exit(1)
