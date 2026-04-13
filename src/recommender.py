from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genres: List[str]
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    liked_song_ids: List[int] = field(default_factory=list)
    disliked_song_ids: List[int] = field(default_factory=list)

def score_song(song: Song, user: UserProfile) -> float:
    """
    Content-based score: how well does this song match the user's taste profile?
    Higher is better. Each feature contributes a weighted component.
    """
    score = 0.0

    # Genre match is the strongest signal (like Pandora's genome weighting)
    if song.genre in user.favorite_genres:
        score += 3.0

    # Mood match
    if song.mood == user.favorite_mood:
        score += 2.0

    # Energy proximity: penalize songs far from the user's target energy
    energy_diff = abs(song.energy - user.target_energy)
    score += (1.0 - energy_diff)

    # Acoustic preference
    if user.likes_acoustic and song.acousticness > 0.6:
        score += 1.0
    elif not user.likes_acoustic and song.acousticness < 0.4:
        score += 1.0

    # Boost songs from genres the user has explicitly liked before
    if hasattr(user, "liked_song_ids") and song.id in user.liked_song_ids:
        score += 5.0  # Already liked — strong signal

    # Penalize explicitly disliked songs so they never surface
    if hasattr(user, "disliked_song_ids") and song.id in user.disliked_song_ids:
        score -= 10.0

    return score


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = [(song, score_song(song, user)) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []

        if song.genre in user.favorite_genres:
            reasons.append(f"matches your favorite genre ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"fits your preferred mood ({song.mood})")

        energy_diff = abs(song.energy - user.target_energy)
        if energy_diff < 0.2:
            reasons.append("has a similar energy level to what you like")

        if user.likes_acoustic and song.acousticness > 0.6:
            reasons.append("is acoustic, which you prefer")
        elif not user.likes_acoustic and song.acousticness < 0.4:
            reasons.append("has the electric/produced sound you like")

        if not reasons:
            reasons.append("has a combination of features similar to your taste")

        return "Recommended because it " + ", and ".join(reasons) + "."

def load_songs(csv_path: str) -> List[Song]:
    """
    Loads songs from a CSV file and returns a list of Song objects.
    Required by src/main.py
    """
    import csv
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(Song(
                id=int(row["id"]),
                title=row["title"],
                artist=row["artist"],
                genre=row["genre"],
                mood=row["mood"],
                energy=float(row["energy"]),
                tempo_bpm=float(row["tempo_bpm"]),
                valence=float(row["valence"]),
                danceability=float(row["danceability"]),
                acousticness=float(row["acousticness"]),
            ))
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Song], k: int = 5) -> List[Tuple[Song, float, str]]:
    """
    Functional wrapper around the Recommender class.
    Converts a raw user_prefs dict into a UserProfile and returns ranked results.
    Required by src/main.py
    """
    user = UserProfile(
        favorite_genres=user_prefs.get("genres", [user_prefs.get("genre", "")]),
        favorite_mood=user_prefs.get("mood", ""),
        target_energy=user_prefs.get("energy", 0.5),
        likes_acoustic=user_prefs.get("likes_acoustic", False),
    )
    rec = Recommender(songs)
    top_songs = rec.recommend(user, k=k)
    return [(song, score_song(song, user), rec.explain_recommendation(user, song)) for song in top_songs]
