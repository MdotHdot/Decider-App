# Movie Decider — Exercises

Work through these in order. Earlier ones are done; new ones build on advanced search and the repo setup.

## What's working now

| Part | Status |
|------|--------|
| CLI (`main.py`) | Mood, genre, duration filters |
| GUI single filters | Mood, genre, duration |
| Advanced Search screen | UI + combined search (with one bug — Exercise 5) |
| Movie database | 28 films with genre, mood, duration, rating, year |
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

**File:** `main.py`

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

## Quick reference

```python
recommender.recommend(
    mood="intense",           # or None to skip
    genre="Comedy",           # or None to skip
    time_available=120,       # or None to skip
    min_rating=8.0,           # Exercise 7
)
```

Happy building 🍿
