# Run Movie Decider on Android

The phone app is the **Kivy GUI** (`main.py`). The CLI (`cli.py`) and TMDB online search stay on your computer for now.

## What you’ll get

- An installable **debug APK** (not Play Store–signed)
- Mood / Genre / Duration / Advanced Search from the existing GUI
- Local 28-film database only (no online search on phone yet — Exercise 16)

## Recommended path: GitHub Actions (no Docker on your Mac)

You don’t have Docker installed, and Buildozer on macOS Apple Silicon is painful. Use CI instead:

1. Commit and push this branch (includes `buildozer.spec` + workflow).
2. On GitHub: **Actions** → **Build Android APK** → **Run workflow**.
3. Wait for the job (first run can take **30–90 minutes** while it downloads the Android SDK/NDK).
4. Open the finished run → **Artifacts** → download `movie-decider-apk`.
5. Copy the `.apk` to your phone (AirDrop, Drive, USB, etc.).
6. On the phone: allow **Install unknown apps** for your file manager/browser, then open the APK.

### Install tips

- If Android blocks it: Settings → Apps → Special access → Install unknown apps.
- This is a **debug** build for feel-testing, not a store release.

## Alternative: Docker on your Mac

1. Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. From the project folder (avoid relying on spaces in the path if mounts fail):

```bash
docker pull kivy/buildozer:latest
docker run --interactive --tty --rm \
  --volume "$HOME/.buildozer":/home/user/.buildozer \
  --volume "$PWD":/home/user/hostcwd \
  kivy/buildozer android debug
```

3. Find the APK under `bin/`.

## Project entry points

| File | Purpose |
|------|---------|
| `main.py` | GUI — required by Buildozer / Android |
| `app.py` | Same GUI (desktop convenience) |
| `cli.py` | Terminal app + TMDB search |
| `buildozer.spec` | Android package settings |

## After you try it on the phone

Note what feels awkward (button size, scrolling, text size, portrait layout). We can tune `decider.kv` for mobile next, then add online search to the GUI (Exercise 16).
