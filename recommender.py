from movies_db import MOVIES


class MovieRecommender:
    """Recommends movies based on mood, genre, and time available."""

    def __init__(self, movies=None):
        self.movies = movies or MOVIES

    def filter_by_mood(self, mood):
        """Filter movies that match the specified mood."""
        return [m for m in self.movies if mood.lower() in [x.lower() for x in m["mood"]]]

    def filter_by_genre(self, genre):
        """Filter movies by genre."""
        return [m for m in self.movies if m["genre"].lower() == genre.lower()]

    def filter_by_duration(self, max_minutes):
        """Filter movies that fit within available time."""
        return [m for m in self.movies if m["duration"] <= max_minutes]
    
    def filter_by_rating(self, min_rating):
        """filter movies byt the rating"""
        return [m for m in self.movies if m["rating"] >= min_rating]

    def recommend(self, mood=None, genre=None, time_available=None, min_rating=None):
        """
        Get movie recommendations based on criteria.

        Args:
            mood: User's current mood (e.g., "intense", "lighthearted")
            genre: Preferred genre (e.g., "Drama", "Action")
            time_available: Minutes available to watch
            min_rating: Minimum rating (Exercise 7 — not wired up yet)

        Returns:
            List of recommended movies sorted by rating
        """
        candidates = self.movies.copy()

        if mood:
            candidates = self.filter_by_mood(mood)

        if genre:
            candidates = [m for m in candidates if m["genre"].lower() == genre.lower()]

        if time_available:
            candidates = [m for m in candidates if m["duration"] <= time_available]

        if min_rating:
             candidates = [m for m in candidates if m["rating"] >= min_rating]

        return sorted(candidates, key=lambda x: x["rating"], reverse=True)

    def get_moods(self):
        """Get all available moods in database."""
        moods = set()
        for movie in self.movies:
            moods.update(movie["mood"])
        return sorted(moods)

    def get_genres(self):
        """Get all available genres in database."""
        genres = set()
        for movie in self.movies:
            genres.add(movie["genre"])
        return sorted(genres)
    
    def get_ratings(self):
        """Get all available ratings in the database."""
        ratings = set()
        for movie in self.movies:
            ratings.add(movie["rating"])
        return sorted(ratings)
