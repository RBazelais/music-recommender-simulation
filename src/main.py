"""
Command line runner for the Music Recommender Simulation.

Demonstrates the full cold-start solution:
  1. Onboarding  — user selects genres they like
  2. Bootstrap   — show popular songs from those genres
  3. Feedback    — user rates each song (y/n)
  4. Refine      — profile updates based on what they liked
  5. Recommend   — personalized recommendations using refined profile
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.recommender import (
    load_songs,
    get_unique_genres,
    onboard_user,
    get_popular_songs_by_genre,
    collect_feedback,
    refine_user_profile,
    recommend_songs,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    songs = load_songs(os.path.join(PROJECT_ROOT, "data", "songs.csv"))

    # --- Step 1: Onboarding ---
    genres = get_unique_genres(songs)
    print("\nWelcome to MoodMatch!")
    print(f"Available genres: {', '.join(genres)}")
    raw = input("Pick genres you like (comma-separated): ")
    selected = [g.strip() for g in raw.split(",") if g.strip() in genres]

    if not selected:
        print("No valid genres selected. Using all genres.")
        selected = genres

    user = onboard_user(selected)
    print(f"\nGot it! Building your starter playlist from: {', '.join(selected)}\n")

    # --- Step 2: Bootstrap with popular songs ---
    bootstrap = get_popular_songs_by_genre(songs, selected, k=5)

    if not bootstrap:
        print("No songs found for those genres.")
        return

    # --- Step 3: Collect feedback ---
    print("Rate each song so we can learn your taste (y = like, n = dislike):\n")
    for song in bootstrap:
        print(f"  {song.title} by {song.artist} [{song.genre} / {song.mood}]")
        answer = input("  Like it? (y/n): ").strip().lower()
        collect_feedback(user, song, liked=(answer == "y"))
        print()

    # --- Step 4: Refine profile ---
    refine_user_profile(user, songs)

    # --- Step 5: Personalized recommendations ---
    print("Based on your feedback, here's what we think you'll love:\n")
    results = recommend_songs(
        {
            "genres": user.favorite_genres,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        },
        songs,
        k=5,
    )

    for song, score, explanation in results:
        if song.id in user.liked_song_ids or song.id in user.disliked_song_ids:
            continue  # skip songs they already rated
        print(f"  {song.title} by {song.artist}")
        print(f"  Score: {score:.2f}")
        print(f"  {explanation}")
        print()


if __name__ == "__main__":
    main()
