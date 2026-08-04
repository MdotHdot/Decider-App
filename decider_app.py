#!/usr/bin/env python3
"""Kivy GUI for the Movie Decision Helper."""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import ListProperty, StringProperty, NumericProperty
from kivy.clock import Clock

from recommender import MovieRecommender


class MovieListItem(BoxLayout):
    title = StringProperty("")
    genre = StringProperty("")
    duration = NumericProperty(0)
    rating = NumericProperty(0)
    mood = StringProperty("")


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
        self.status_text = "Set your filters, then tap Search."

    def submit(self):
        app = App.get_running_app()
        recommender = app.recommender
        result_screen = self.manager.get_screen("result")

        mood = self.ids.adv_mood_spinner.text
        genre = self.ids.adv_genre_spinner.text

        try:
            time_available = int(self.ids.adv_duration_input.text)
        except ValueError:
            self.status_text = "Please enter a valid number for duration"
            return

        # TODO (Exercise 5): When spinner shows "Any", pass None instead of "Any"
        # so that filter is skipped. Right now "Any" is passed as a string and
        # won't match anything — fix _resolve_filter below.
        mood_arg = self._resolve_filter(mood)
        genre_arg = self._resolve_filter(genre)

        recommendations = recommender.recommend(
            mood=mood_arg,
            genre=genre_arg,
            time_available=time_available,
        )

        # TODO (Exercise 6): Update status_text to show match count before navigating,
        # e.g. "Found 3 matches" — only if you want feedback on this screen first.

        result_screen.show_results(recommendations, "advanced search")
        self.manager.current = "result"

    def _resolve_filter(self, value):
        """Convert spinner value to a recommend() argument.

        TODO (Exercise 5): Return None when value is "Any", otherwise return value.
        Currently broken on purpose — "Any" gets passed through as a string.
        """
        return value  # <-- your fix goes here


class ResultScreen(Screen):
    result_text = StringProperty("")
    recommendations = ListProperty([])

    def show_results(self, recommendations, filter_type):
        self.recommendations = recommendations
        if recommendations:
            top = recommendations[0]
            self.result_text = (
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


class DeciderRoot(ScreenManager):
    pass


class DeciderApp(App):
    def build(self):
        self.recommender = MovieRecommender()
        root = DeciderRoot()
        main_screen = root.get_screen("main")
        main_screen.movies = self.recommender.movies
        return root


if __name__ == "__main__":
    DeciderApp().run()
