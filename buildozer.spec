[app]

# (str) Title of your application
title = Movie Decider

# (str) Package name
package.name = moviedecider

# (str) Package domain (needed for android/ios packaging)
package.domain = org.mdothdot

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (list) Source files to exclude
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .venv, kivy_venv, venv, .buildozer, __pycache__, .github
# Keep CLI/TMDB modules out of the APK so p4a does not pull requests/bs4
source.exclude_patterns = license,images/*/*.jpg,.git/*,*.md,cli.py,film_search.py

# (str) Application versioning (method 1)
version = 0.1.0

# (list) Application requirements — GUI only for phone feel-test
requirements = python3,kivy

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET

# (int) Target Android API
android.api = 33

# (int) Minimum API your APK / AAB will support
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Accept Android SDK license
android.accept_sdk_license = True

# Single arch for faster CI (covers modern phones including yours)
android.archs = arm64-v8a

# Stable p4a branch = Python <= 3.12 (avoid develop/Python 3.14 breakage)
p4a.branch = master

# (bool) Skip Android packaging if only Python files changed
android.skip_update = False

# (str) The format used to package the app for debug mode (apk or aar)
android.debug_artifact = apk

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1
