"""Online film search via TMDB API, plus an IMDb scrape skeleton for Exercise 13."""

from __future__ import annotations

import os
from typing import Any

import requests

TMDB_BASE = "https://api.themoviedb.org/3"
DEFAULT_TIMEOUT = 10


class FilmSearchError(Exception):
    """Raised when an online search fails."""


def get_api_key(api_key: str | None = None) -> str:
    """Return a TMDB API key from the argument or TMDB_API_KEY env var."""
    key = api_key or os.environ.get("TMDB_API_KEY", "").strip()
    if not key:
        raise FilmSearchError(
            "Missing TMDB API key. Set TMDB_API_KEY in your environment "
            "(see README.md)."
        )
    return key


def search_tmdb(query: str, api_key: str | None = None, limit: int = 8) -> list[dict]:
    """
    Search TMDB for movies matching query.

    Returns a list of Decider-shaped movie dicts (duration/genre may be incomplete
    until fetch_tmdb_details is called).
    """
    query = (query or "").strip()
    if not query:
        raise FilmSearchError("Search query cannot be empty.")

    key = get_api_key(api_key)
    url = f"{TMDB_BASE}/search/movie"
    params = {
        "api_key": key,
        "query": query,
        "include_adult": "false",
        "language": "en-US",
        "page": 1,
    }

    try:
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FilmSearchError(f"TMDB search failed: {exc}") from exc

    results = response.json().get("results") or []
    movies = []
    for item in results[:limit]:
        movies.append(normalize_tmdb_result(item))
    return movies


def fetch_tmdb_details(movie_id: int, api_key: str | None = None) -> dict:
    """Fetch full TMDB movie details (runtime, genres, etc.)."""
    key = get_api_key(api_key)
    url = f"{TMDB_BASE}/movie/{movie_id}"
    params = {"api_key": key, "language": "en-US"}

    try:
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FilmSearchError(f"TMDB details failed: {exc}") from exc

    return response.json()


def normalize_tmdb_result(item: dict[str, Any], details: dict[str, Any] | None = None) -> dict:
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
        "source": "tmdb",
        "tmdb_id": tmdb_id,
        "overview": (source.get("overview") or item.get("overview") or "").strip(),
    }


def enrich_with_details(movie: dict, api_key: str | None = None) -> dict:
    """Fetch TMDB details for a search result and return an updated movie dict."""
    tmdb_id = movie.get("tmdb_id")
    if not tmdb_id:
        raise FilmSearchError("Movie is missing tmdb_id; cannot fetch details.")
    details = fetch_tmdb_details(int(tmdb_id), api_key=api_key)
    return normalize_tmdb_result(movie, details=details)


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
