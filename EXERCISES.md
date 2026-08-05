# Movie Decider — Exercises

Work through these in order. Earlier ones are done; new ones build on advanced search and the repo setup.

## What's working now

| Part | Status |
|------|--------|
| CLI (`cli.py`) | Mood, genre, duration filters |
| GUI single filters | Mood, genre, duration |
| Advanced Search screen | UI + combined search (with one bug — Exercise 5) |
| Movie database | 28 films with genre, mood, duration, rating, year |
| Online search (TMDB) | CLI option 7 — requires `TMDB_API_KEY` |
| IMDb scraper | Skeleton only — Exercise 13 |
| Repo setup | `.gitignore`, `requirements.txt`, own git root |

---

## Exercise 5 — Fix "Any" in Advanced Search (~10 min)

**File:** `decider_app.py` → `AdvancedSearchScreen._resolve_filter()`

**Problem:** When you pick **Any** for mood or genre, the app passes the string `"Any"` to `recommend()`, which tries to find movies with mood `"Any"` — and finds nothing.

**Goal:** Skip that filter when the user picks Any.

**Hint:**

```python
def _resolve_filter(self, value):
    if value == "Any":
        return None  # None = skip this filter
    return value
```

**Test:**
- Mood: **Any**, Genre: **Comedy**, Duration: **120** → should show comedies under 120 min
- Mood: **intense**, Genre: **Any**, Duration: **150** → intense films under 150 min

---

## Exercise 6 — Show match count on Advanced Search (~15 min)

**File:** `decider_app.py` → `AdvancedSearchScreen.submit()`

**Goal:** Before going to the results screen, set `status_text` to something like `"Found 3 matches"`.

If zero matches, set status and **stay** on the advanced screen instead of navigating away.

---

## Exercise 7 — Minimum rating filter (~25 min)

**Files:** `recommender.py`, `decider.kv`, `decider_app.py`

1. Uncomment and finish the `min_rating` block in `recommend()`.
2. Add a `TextInput` or `Spinner` on the Advanced Search screen for minimum rating (e.g. 7.0, 8.0, Any).
3. Pass `min_rating` from `AdvancedSearchScreen.submit()`.

**Test:** Mood Any, Genre Any, Duration 200, Min rating 8.5 → only top-tier films.

---

## Exercise 8 — "Surprise me" button (~20 min)

**File:** `decider_app.py` + `decider.kv`

Add a button on the **Result** screen: **Surprise me**.

When tapped, pick a **random** film from `self.recommendations` (use `import random`) and update `result_text` to highlight that pick.

---

## Exercise 9 — Advanced search in CLI (~30 min)

**File:** `cli.py`

Add menu option **6. Advanced search** that asks for mood, genre, and duration (allow blank/Enter to skip), then calls `recommend()` with the combined criteria.

Reuse the same "Any"/empty → `None` logic from Exercise 5.

---

## Exercise 10 — Add your films (~15 min)

**File:** `movies_db.py`

Add at least **5 films you love**. Each needs:

```python
{
    "title": "...",
    "genre": "...",
    "mood": ["...", "..."],
    "duration": 120,
    "rating": 8.0,
    "year": 2020,
},
```

---

## Exercise 11 — Load movies from JSON (stretch)

**Files:** new `movies.json`, update `movies_db.py`

Move the movie list into `movies.json` and load it with:

```python
import json
from pathlib import Path

def load_movies():
    path = Path(__file__).parent / "movies.json"
    with open(path) as f:
        return json.load(f)

MOVIES = load_movies()
```

---

## Exercise 12 — Remember last search (stretch)

Save the last advanced search to `preferences.json` on submit, reload in `on_enter`.

---

## Exercise 13 — Finish IMDb scrape (~45 min)

**File:** `film_search.py` → `scrape_imdb_search()`

**Goal:** Practice BeautifulSoup. Prefer TMDB for real use — IMDb HTML breaks often.

**Steps:**

1. Use `requests.get` on `https://www.imdb.com/find/?q=<query>&s=tt`
2. Send a browser-like `User-Agent` header (IMDb often rejects default Python agents)
3. Parse HTML with `BeautifulSoup(html, "html.parser")`
4. Find result rows (inspect the page in DevTools — selectors change)
5. For each hit, extract title and year into a Decider-shaped dict with `"source": "imdb"`
6. Remove the `raise NotImplementedError`

**Optional:** In CLI option 7, ask `tmdb` vs `imdb` and call your scraper when chosen.

---

## Exercise 14 — Guess moods for online films (~30 min)

**File:** `film_search.py`

Online films currently have `"mood": []`, so mood filters ignore them.

**Goal:** Add `guess_moods(genre, overview)` that returns a short list of mood tags from keywords, e.g.:

- genre Horror → `["dark", "suspenseful"]`
- overview contains "love" → add `"romantic"`

Call it from `normalize_tmdb_result`.

---

## Exercise 15 — Persist added films (~30 min)

**Files:** new `movies.json` and/or `movies_db.py`

When the user adds a TMDB film in CLI option 7, save it so the next run still has it.

**Approach:** Append to `movies.json` (or rewrite the list), then load that file in `movies_db.py` (see Exercise 11).

---

## Exercise 16 — GUI Online Search screen (~45 min)

**Files:** `decider_app.py`, `decider.kv`

Add an **Online** button on the main screen that opens a new screen:

1. Text box + Search button
2. Call `search_tmdb` (run network calls carefully — Kivy is single-threaded)
3. Show results; tap one to enrich + optionally merge into `app.recommender.movies`

---

## Quick reference

```python
recommender.recommend(
    mood="intense",           # or None to skip
    genre="Comedy",           # or None to skip
    time_available=120,       # or None to skip
    min_rating=8.0,           # Exercise 7
)

from film_search import search_tmdb, enrich_with_details, merge_movies
results = search_tmdb("Inception")   # needs TMDB_API_KEY
detailed = enrich_with_details(results[0])
```

Happy building 🍿
