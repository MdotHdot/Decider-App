#!/usr/bin/env python3
"""Kivy GUI for the Movie Decision Helper."""

import json
import random
import threading
from pathlib import Path

from kivy.app import App
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import BooleanProperty, ListProperty, StringProperty, NumericProperty
from kivy.clock import Clock

from film_search import (
    DEFAULT_PROVIDER,
    PROVIDERS,
    FilmSearchError,
    check_api_key,
    enrich_with_details,
    merge_movies,
    search_tmdb,
)
from recommender import MovieRecommender


class MovieListItem(BoxLayout):
    title = StringProperty("")
    genre = StringProperty("")
    duration = NumericProperty(0)
    rating = NumericProperty(0)
    mood = StringProperty("")


class OnlineResultItem(ButtonBehavior, MovieListItem):
    """Tappable search hit; index points into OnlineScreen.results."""

    index = NumericProperty(0)


class WelcomeScreen(Screen):
    pass


class MainScreen(Screen):
    """Browse all movies and pick a filter type."""

    movies = ListProperty([])
    selected = StringProperty("Tap Mood, Genre, Duration, or Advanced Search.")

    def on_enter(self):
        self.refresh_movie_list()

    def refresh_movie_list(self):
        grid = self.ids.movies_grid
        grid.clear_widgets()
        for movie in sorted(self.movies, key=lambda x: x["rating"], reverse=True):
            grid.add_widget(
                MovieListItem(
                    title=movie["title"],
                    genre=movie["genre"],
                    duration=movie["duration"],
                    rating=movie["rating"],
                    mood=", ".join(movie["mood"]),
                )
            )

    def open_filter(self, filter_type):
        input_screen = self.manager.get_screen("input")
        input_screen.setup(filter_type)
        self.manager.current = "input"


class InputScreen(Screen):
    """Single-filter screens for mood, genre, or duration."""

    filter_type = StringProperty("mood")
    prompt_text = StringProperty("")

    def setup(self, filter_type):
        self.filter_type = filter_type
        app = App.get_running_app()
        recommender = app.recommender

        if filter_type == "mood":
            self.prompt_text = "How are you feeling?"
            self.ids.mood_spinner.values = recommender.get_moods()
            if self.ids.mood_spinner.values:
                self.ids.mood_spinner.text = self.ids.mood_spinner.values[0]
            self.ids.mood_panel.opacity = 1
            self.ids.mood_panel.disabled = False
            self.ids.genre_panel.opacity = 0
            self.ids.genre_panel.disabled = True
            self.ids.duration_panel.opacity = 0
            self.ids.duration_panel.disabled = True

        elif filter_type == "genre":
            self.prompt_text = "What genre are you thinking?"
            self.ids.genre_spinner.values = recommender.get_genres()
            if self.ids.genre_spinner.values:
                self.ids.genre_spinner.text = self.ids.genre_spinner.values[0]
            self.ids.mood_panel.opacity = 0
            self.ids.mood_panel.disabled = True
            self.ids.genre_panel.opacity = 1
            self.ids.genre_panel.disabled = False
            self.ids.duration_panel.opacity = 0
            self.ids.duration_panel.disabled = True

        elif filter_type == "duration":
            self.prompt_text = "How much time do you have? (minutes)"
            self.ids.duration_input.text = "120"
            self.ids.mood_panel.opacity = 0
            self.ids.mood_panel.disabled = True
            self.ids.genre_panel.opacity = 0
            self.ids.genre_panel.disabled = True
            self.ids.duration_panel.opacity = 1
            self.ids.duration_panel.disabled = False

    def submit(self):
        app = App.get_running_app()
        recommender = app.recommender
        result_screen = self.manager.get_screen("result")

        if self.filter_type == "mood":
            recommendations = recommender.recommend(mood=self.ids.mood_spinner.text)

        elif self.filter_type == "genre":
            recommendations = recommender.recommend(genre=self.ids.genre_spinner.text)

        elif self.filter_type == "duration":
            try:
                time_available = int(self.ids.duration_input.text)
                recommendations = recommender.recommend(time_available=time_available)
            except ValueError:
                self.prompt_text = "Please enter a valid number"
                return
        else:
            recommendations = []

        result_screen.show_results(recommendations, self.filter_type)
        self.manager.current = "result"


class AdvancedSearchScreen(Screen):
    """Combine mood, genre, and duration to refine results."""

    status_text = StringProperty("Set your filters, then tap Search.")

    def on_enter(self):
        app = App.get_running_app()
        recommender = app.recommender

        moods = ["Any"] + recommender.get_moods()
        genres = ["Any"] + recommender.get_genres()

        self.ids.adv_mood_spinner.values = moods
        self.ids.adv_mood_spinner.text = "Any"
        self.ids.adv_genre_spinner.values = genres
        self.ids.adv_genre_spinner.text = "Any"
        self.ids.adv_duration_input.text = "150"
        self.ids.adv_rating_input.text = "Any"
        self.status_text = "Set your filters, then tap Search."

    def submit(self):
        app = App.get_running_app()
        recommender = app.recommender
        result_screen = self.manager.get_screen("result")

        mood = self.ids.adv_mood_spinner.text
        genre = self.ids.adv_genre_spinner.text
        rating_text = self.ids.adv_rating_input.text.strip()

        try:
            time_available = int(self.ids.adv_duration_input.text)
        except ValueError:
            self.status_text = "Please enter a valid number for duration"
            return

        # "Any" / blank → skip rating filter; otherwise parse as float
        if rating_text.lower() in ("", "any"):
            min_rating = None
        else:
            try:
                min_rating = float(rating_text)
            except ValueError:
                self.status_text = "Please enter a valid rating (e.g. 8.5) or Any"
                return

        mood_arg = self._resolve_filter(mood)
        genre_arg = self._resolve_filter(genre)

        recommendations = recommender.recommend(
            mood=mood_arg,
            genre=genre_arg,
            time_available=time_available,
            min_rating=min_rating,
        )

        count = len(recommendations)
        if count >= 1:
            self.status_text = f"Found {count} matches"
            
            result_screen.show_results(recommendations, "advanced search")
            self.manager.current = "result"
        
        else:
            self.status_text = "No movies matched your criteria."
    
    def _resolve_filter(self, value):
        """Resolves genre and mood if any filter to be skipped."""
        
        if value == "Any":
            return None
        else:
            return value
        
class ResultScreen(Screen):
    result_text = StringProperty("")
    recommendations = ListProperty([])

    def show_results(self, recommendations, filter_type):
        self.recommendations = recommendations
        if recommendations:           
            top = recommendations[0]
            self.result_text = (
                f"there is {len(recommendations)} matching your criteria!\n"
                f"Top pick: {top['title']}\n"
                f"{top['genre']} · {top['duration']} min · {top['rating']}/10\n"
                f"Moods: {', '.join(top['mood'])}"
            )
        else:
            self.result_text = f"No movies matched your {filter_type} filter."

        Clock.schedule_once(self._populate_list, 0)

    def _populate_list(self, _dt):
        grid = self.ids.results_grid
        grid.clear_widgets()
        for movie in self.recommendations:
            grid.add_widget(
                MovieListItem(
                    title=movie["title"],
                    genre=movie["genre"],
                    duration=movie["duration"],
                    rating=movie["rating"],
                    mood=", ".join(movie["mood"]),
                )
            )

    def surprise_me(self):
        if not self.recommendations:
            self.result_text = "No films to surprise you with."
            return

        pick = random.choice(self.recommendations)

        self.result_text = (
            f"Surprise pick: {pick['title']}\n"
            f"{pick['genre']} · {pick['duration']} min · {pick['rating']}/10\n"
            f"Moods: {', '.join(pick['mood'])}"   
        )
        
class OnlineScreen(Screen):
    """Search a TMDB-compatible API, preview a film, and add it to this session."""

    status_text = StringProperty("Enter your API key once, then search for a film.")
    detail_text = StringProperty("")
    provider = StringProperty(DEFAULT_PROVIDER)
    provider_ids = ListProperty(list(PROVIDERS))
    busy = BooleanProperty(False)
    results = ListProperty([])
    selected = None

    def on_enter(self):
        settings = App.get_running_app().settings
        self.provider = settings.get("provider", DEFAULT_PROVIDER)
        self.ids.api_key_input.text = settings.get("api_key", "")

    def attribution_text(self, provider):
        if provider == "tmdb":
            return "This product uses the TMDB API but is not endorsed or certified by TMDB."
        return f"Movie data from {PROVIDERS[provider]['name']}."

    def _credentials(self):
        return {
            "api_key": self.ids.api_key_input.text.strip() or None,
            "provider": self.provider,
        }

    def save_key(self):
        App.get_running_app().save_settings(
            provider=self.provider,
            api_key=self.ids.api_key_input.text.strip(),
        )
        self.status_text = f"Saved {PROVIDERS[self.provider]['name']} key on this device."

    def test_key(self):
        self.status_text = "Checking key..."
        self._run_in_background(check_api_key, self._on_key_ok, **self._credentials())

    def _on_key_ok(self, provider_name):
        self.status_text = f"{provider_name} key works. Tap Save to keep it."

    def search_online(self):
        query = self.ids.online_query.text.strip()
        if not query:
            self.status_text = "Enter a movie title."
            return
        self.status_text = f"Searching for '{query}'..."
        self._run_in_background(
            search_tmdb, lambda results: self._show_results(query, results),
            query, **self._credentials(),
        )

    def _show_results(self, query, results):
        self.results = results
        self.selected = None
        self.detail_text = ""

        grid = self.ids.online_results_grid
        grid.clear_widgets()
        if not results:
            self.status_text = f"No results for '{query}'."
            return

        self.status_text = f"Found {len(results)} films. Tap one for details."
        for index, movie in enumerate(results):
            grid.add_widget(
                OnlineResultItem(
                    index=index,
                    title=f"{movie['title']} ({movie['year'] or '?'})",
                    genre=movie.get("genre") or "—",
                    duration=movie.get("duration") or 0,
                    rating=movie.get("rating") or 0,
                    mood=", ".join(movie.get("mood") or []),
                )
            )

    def select_result(self, index):
        movie = self.results[int(index)]
        self.status_text = f"Loading details for {movie['title']}..."
        self._run_in_background(enrich_with_details, self._show_detail, movie, **self._credentials())

    def _show_detail(self, movie):
        self.selected = movie
        overview = movie.get("overview") or ""
        if len(overview) > 200:
            overview = overview[:200].rsplit(" ", 1)[0] + "..."
        self.detail_text = (
            f"{movie['title']} ({movie['year'] or '?'})\n"
            f"{movie['genre']} · {movie['duration']} min · {movie['rating']}/10\n"
            f"{overview}"
        )
        self.status_text = "Tap 'Add to my list' to use it in filters."

    def add_selected(self):
        if not self.selected:
            self.status_text = "Pick a film first."
            return
        app = App.get_running_app()
        before = len(app.recommender.movies)
        app.recommender.movies = merge_movies(app.recommender.movies, [self.selected])
        self.manager.get_screen("main").movies = app.recommender.movies

        if len(app.recommender.movies) == before:
            self.status_text = f"'{self.selected['title']}' is already in your list."
        else:
            self.status_text = (
                f"Added '{self.selected['title']}'. "
                f"Your list now has {len(app.recommender.movies)} films."
            )

    def _run_in_background(self, func, on_success, *args, **kwargs):
        """Run a network call off the UI thread; Kivy widgets may only change on the main thread."""
        if self.busy:
            return
        self.busy = True

        def worker():
            try:
                result = func(*args, **kwargs)
            except FilmSearchError as exc:
                message = str(exc)
                Clock.schedule_once(lambda _dt: self._on_error(message))
                return
            except Exception as exc:
                message = f"Unexpected error: {type(exc).__name__}"
                Clock.schedule_once(lambda _dt: self._on_error(message))
                return
            Clock.schedule_once(lambda _dt: self._on_done(on_success, result))

        threading.Thread(target=worker, daemon=True).start()

    def _on_done(self, on_success, result):
        self.busy = False
        on_success(result)

    def _on_error(self, message):
        self.busy = False
        self.status_text = message


class DeciderRoot(ScreenManager):
    pass


class DeciderApp(App):
    settings = {}

    def build(self):
        self.settings = self.load_settings()
        self.recommender = MovieRecommender()
        root = DeciderRoot()
        main_screen = root.get_screen("main")
        main_screen.movies = self.recommender.movies
        return root

    @property
    def settings_path(self):
        return Path(self.user_data_dir) / "settings.json"

    def load_settings(self):
        try:
            return json.loads(self.settings_path.read_text())
        except (OSError, ValueError):
            return {}

    def save_settings(self, **changes):
        self.settings = {**self.settings, **changes}
        self.settings_path.write_text(json.dumps(self.settings))


if __name__ == "__main__":
    DeciderApp().run()
