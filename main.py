#!/usr/bin/env python3
"""
Movie Recommendation App - CLI Interface
Helps users decide what movie to watch based on mood, genre, and time available.
"""

from recommender import MovieRecommender


def print_separator():
    print("\n" + "=" * 60 + "\n")


def display_movie(movie, index=None):
    """Display movie details in a formatted way."""
    prefix = f"{index}. " if index else "→ "
    print(f"{prefix}{movie['title']}")
    print(f"   Genre: {movie['genre']} | Duration: {movie['duration']} min | Rating: {movie['rating']}/10")
    print(f"   Moods: {', '.join(movie['mood'])}")


def interactive_mode():
    """Run the app in interactive mode."""
    recommender = MovieRecommender()
    
    print_separator()
    print("🎬 MOVIE DECISION HELPER 🎬")
    print_separator()
    
    print("Welcome! I'll help you pick a movie to watch.")
    print("\nAvailable options:")
    print("1. Get recommendations by mood")
    print("2. Get recommendations by genre")
    print("3. Get recommendations by time available")
    print("4. Browse all movies")
    print("5. Exit")
    print("6. Advanced search  (Exercise 9 — not implemented yet)")
    
    while True:
        print_separator()
        choice = input("What would you like to do? (1-5): ").strip()
        
        if choice == "1":
            print("\nAvailable moods:", ", ".join(recommender.get_moods()))
            mood = input("Enter your mood: ").strip()
            recommendations = recommender.filter_by_mood(mood)
            
            if recommendations:
                print(f"\n📽️ Movies for mood '{mood}':")
                for i, movie in enumerate(sorted(recommendations, key=lambda x: x["rating"], reverse=True), 1):
                    display_movie(movie, i)
            else:
                print(f"No movies found for mood '{mood}'")
        
        elif choice == "2":
            print("\nAvailable genres:", ", ".join(recommender.get_genres()))
            genre = input("Enter your preferred genre: ").strip()
            recommendations = recommender.filter_by_genre(genre)
            
            if recommendations:
                print(f"\n📽️ Movies in genre '{genre}':")
                for i, movie in enumerate(sorted(recommendations, key=lambda x: x["rating"], reverse=True), 1):
                    display_movie(movie, i)
            else:
                print(f"No movies found in genre '{genre}'")
        
        elif choice == "3":
            try:
                time_available = int(input("How many minutes do you have? ").strip())
                recommendations = recommender.filter_by_duration(time_available)
                
                if recommendations:
                    print(f"\n📽️ Movies you can watch in {time_available} minutes:")
                    for i, movie in enumerate(sorted(recommendations, key=lambda x: x["rating"], reverse=True), 1):
                        display_movie(movie, i)
                else:
                    print(f"No movies found that fit in {time_available} minutes")
            except ValueError:
                print("Please enter a valid number")
        
        elif choice == "4":
            print("\n📽️ All available movies:")
            for i, movie in enumerate(sorted(recommender.movies, key=lambda x: x["rating"], reverse=True), 1):
                display_movie(movie, i)
        
        elif choice == "5":
            print("\nHappy watching! 🍿")
            break

        elif choice == "6":
            # TODO (Exercise 9): Ask for mood, genre, duration (blank = skip)
            # then call recommender.recommend() — see EXERCISES.md
            print("\nExercise 9: Implement advanced search here! See EXERCISES.md")
        
        else:
            print("Invalid choice. Please enter 1-6.")


def get_quick_recommendation(mood=None, genre=None, time_available=None):
    """Get a quick recommendation without interactive prompts."""
    recommender = MovieRecommender()
    recommendations = recommender.recommend(mood=mood, genre=genre, time_available=time_available)
    
    if recommendations:
        print("\n🎬 Top Recommendation:")
        display_movie(recommendations[0])
        
        if len(recommendations) > 1:
            print(f"\n📊 Other options ({len(recommendations) - 1} more):")
            for movie in recommendations[1:4]:  # Show up to 3 more
                display_movie(movie)
    else:
        print("No movies found matching your criteria.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Command line arguments for quick recommendations
        mood = None
        genre = None
        time_available = None
        
        for i, arg in enumerate(sys.argv[1:], 1):
            if arg.startswith("--mood="):
                mood = arg.split("=")[1]
            elif arg.startswith("--genre="):
                genre = arg.split("=")[1]
            elif arg.startswith("--time="):
                try:
                    time_available = int(arg.split("=")[1])
                except ValueError:
                    pass
        
        get_quick_recommendation(mood=mood, genre=genre, time_available=time_available)
    else:
        # Run interactive mode
        interactive_mode()
