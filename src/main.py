"""
Command line runner for the Music Recommender Simulation.

Run modes:
  python -m src.main          — interactive cold-start onboarding
  python -m src.main --demo   — run three preset user profiles and compare outputs
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
    UserProfile,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Three distinct user profiles for the multi-profile demo
# ---------------------------------------------------------------------------
DEMO_PROFILES = [
    {
        "name": "Hip-Hop / EDM Fan",
        "description": "Loves high-energy dance tracks, confident & intense vibes, no acoustic.",
        "prefs": {
            "genres": ["hip-hop", "edm"],
            "mood": "confident",
            "energy": 0.90,
            "likes_acoustic": False,
        },
    },
    {
        "name": "Acoustic Chill Listener",
        "description": "Prefers calm, acoustic folk and lofi; low energy, relaxed mood.",
        "prefs": {
            "genres": ["folk", "lofi", "ambient"],
            "mood": "relaxed",
            "energy": 0.28,
            "likes_acoustic": True,
        },
    },
    {
        "name": "High-Tempo Intensity Seeker",
        "description": "Wants pure intensity — metal, rock, or EDM, high BPM, no chill.",
        "prefs": {
            "genres": ["metal", "rock", "edm"],
            "mood": "intense",
            "energy": 0.95,
            "likes_acoustic": False,
        },
    },
]


def run_demo(songs) -> None:
    """Run all three preset profiles and print ranked recommendations for each."""
    print("\n" + "=" * 60)
    print("  MUSIC RECOMMENDER — MULTI-PROFILE DEMO")
    print("=" * 60)

    for profile in DEMO_PROFILES:
        print(f"\n{'─' * 60}")
        print(f"  Profile: {profile['name']}")
        print(f"  {profile['description']}")
        print(f"{'─' * 60}")

        results = recommend_songs(profile["prefs"], songs, k=5)

        for rank, (song, score, explanation) in enumerate(results, start=1):
            print(f"\n  #{rank}  {song.title} — {song.artist}")
            print(f"       Genre: {song.genre} | Mood: {song.mood} | Energy: {song.energy}")
            print(f"       Score: {score:.2f}")
            print(f"       {explanation}")

    print(f"\n{'=' * 60}")
    print("  OBSERVATIONS")
    print(f"{'=' * 60}")
    print("""
  Hip-Hop / EDM Fan     → top results cluster around high-danceability,
                          high-energy tracks (edm, hip-hop). Acoustic songs
                          score near zero and never appear.

  Acoustic Chill        → recommendations shift entirely to folk, lofi, and
                          ambient. Energy proximity rewards the quietest songs;
                          metal and EDM are effectively excluded.

  High-Tempo Intensity  → metal and rock dominate, with EDM filling remaining
                          slots. The energy score pushes tracks above 0.9 to
                          the top regardless of mood label.
""")


def main() -> None:
    songs = load_songs(os.path.join(PROJECT_ROOT, "data", "songs.csv"))

    if "--demo" in sys.argv:
        run_demo(songs)
        return


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
