# Movie Decider

A Python app to help you pick a film based on **mood**, **genre**, and **time available**. Includes a CLI and a Kivy GUI with an **Advanced Search** screen.

## Project structure

```
.
├── app.py               # GUI entry point
├── decider_app.py       # Kivy screens and logic
├── decider.kv           # Kivy UI layout
├── main.py              # CLI entry point
├── recommender.py       # Recommendation engine
├── movies_db.py         # Movie database (28 films)
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
# CLI
python main.py

# GUI
python app.py
```

## Features

- **Single filters** — mood, genre, or duration alone
- **Advanced Search** — combine all three (fix "Any" in Exercise 5)
- **28 films** — drama, comedy, sci-fi, horror, animation, and more

## Your next steps

Open **`EXERCISES.md`** and start with **Exercise 5** (fix "Any" in advanced search).

| Exercise | What you'll build |
|----------|-------------------|
| 5 | Skip filters when user picks "Any" |
| 6 | Show match count before results |
| 7 | Minimum rating filter |
| 8 | "Surprise me" random pick |
| 9 | Advanced search in CLI |
| 10 | Add your own films |

## CLI quick examples

```bash
python main.py --mood=intense --time=150
python main.py --genre=Comedy
python main.py
```

## Requirements

- Python 3.10+
- Kivy 2.3+ (GUI only — CLI has no dependencies)
