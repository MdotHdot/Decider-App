# Movie Decider

A Python app to help you pick a film based on **mood**, **genre**, and **time available**. Includes a CLI and a Kivy GUI with an **Advanced Search** screen.

## Project structure

```
.
├── main.py              # GUI entry (Android / Buildozer)
├── app.py               # Same GUI (desktop convenience)
├── cli.py               # CLI + TMDB online search
├── decider_app.py       # Kivy screens and logic
├── decider.kv           # Kivy UI layout
├── film_search.py       # TMDB online search (+ IMDb scrape exercise)
├── recommender.py       # Recommendation engine
├── movies_db.py         # Movie database (28 films)
├── buildozer.spec       # Android APK packaging config
├── ANDROID.md           # How to build/install on a phone
├── EXERCISES.md         # Your to-do list — work through these next
├── requirements.txt     # Python dependencies
└── .gitignore
```

## Setup (first time)

This project should be its **own git repo**, separate from the parent `Python/` folder (which may show unrelated changes in VS Code).

### 1. Create a virtual environment

```bash
cd "Python Projects/decider app"
python3 -m venv .venv
source .venv/bin/activate        # macOS/Linux
# .venv\Scripts\activate         # Windows
pip install -r requirements.txt
```

If you already have `kivy_venv/`, you can keep using it or migrate:

```bash
source kivy_venv/bin/activate   # existing
# OR create fresh .venv as above and delete kivy_venv when done
```

### 2. Initialise git (this folder only)

If VS Code shows changes from other projects, the git root is probably the parent folder. Fix it like this:

```bash
cd "Python Projects/decider app"
git init
git add .
git status   # should only show files from this project
```

Then in VS Code: **File → Open Folder** and open the `decider app` folder directly (not the parent `Python` folder).

### 3. Run the app

```bash
# CLI (+ TMDB online search)
python cli.py

# GUI (desktop)
python main.py
# or: python app.py
```

### Android APK (phone feel-test)

See **[ANDROID.md](ANDROID.md)**. Short version: push the branch, run the **Build Android APK** GitHub Action, download the artifact, install on your phone.

### 4. Online search (TMDB or amodb)

Two providers share the same API, so switching is a setting, not a code change:

| Provider | Cost | Allowed |
|----------|------|---------|
| `tmdb` (default) | Free | Non-commercial only: no ads, purchases, or subscriptions. Must show TMDB attribution (the Online screen does). |
| `amodb` | Paid (from ~$5/month) | Commercial use, e.g. once you add ads |

Get a key: TMDB at [Settings → API](https://www.themoviedb.org/settings/api), amodb at [amodb.dev](https://amodb.dev/).

**In the app (desktop or phone):** Main screen → **Online** → pick the provider, paste the key → **Test** → **Save**. The key is stored on that device only (in the app's data folder), never in the code or APK.

**From the terminal (desktop / CLI):**

```bash
export TMDB_API_KEY="your_key_here"        # or: export FILM_API_PROVIDER=amodb AMODB_KEY="..."
python film_search.py Inception            # checks the key and prints 3 results
python cli.py                              # option 7: Search online
```

Never commit a key or paste it into chat; regenerate it if you do.

You can preview results and optionally add a film to the **current session** (not saved to disk yet — Exercise 15).

IMDb scraping is left as **Exercise 13** in `film_search.py` for learning BeautifulSoup.

## Features

- **Single filters** — mood, genre, or duration alone
- **Advanced Search** — combine all three (fix "Any" in Exercise 5)
- **Online search** — TMDB/amodb from the GUI **Online** screen (works on Android) and CLI option 7
- **28 local films** — drama, comedy, sci-fi, horror, animation, and more

## Your next steps

Open **`EXERCISES.md`**. For this branch, start with **Exercise 13** (IMDb scrape) after trying CLI option 7.

| Exercise | What you'll build |
|----------|-------------------|
| 5–12 | Earlier GUI / CLI polish (see EXERCISES.md) |
| 13 | Finish IMDb BeautifulSoup scraper |
| 14 | Guess moods for online films |
| 15 | Persist added films to disk |
| 16 | GUI Online Search screen (done) |

## CLI quick examples

```bash
python cli.py --mood=intense --time=150
python cli.py --genre=Comedy
python cli.py
```

## Requirements

- Python 3.10+
- Kivy 2.3+ (GUI)
- `requests` (TMDB CLI search)
- `beautifulsoup4` (Exercise 13 scraper)
