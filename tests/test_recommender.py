from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    score_song,
    collect_feedback,
    refine_user_profile,
    get_popular_songs_by_genre,
    onboard_user,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def make_songs() -> list:
    return [
        Song(id=1, title="Test Pop Track", artist="A", genre="pop",
             mood="happy", energy=0.8, tempo_bpm=120, valence=0.9,
             danceability=0.8, acousticness=0.2),
        Song(id=2, title="Chill Lofi Loop", artist="B", genre="lofi",
             mood="chill", energy=0.4, tempo_bpm=80, valence=0.6,
             danceability=0.5, acousticness=0.9),
        Song(id=3, title="Rock Storm", artist="C", genre="rock",
             mood="intense", energy=0.95, tempo_bpm=155, valence=0.4,
             danceability=0.6, acousticness=0.05),
    ]


def make_small_recommender() -> Recommender:
    return Recommender(make_songs()[:2])


def make_user(**overrides) -> UserProfile:
    defaults = dict(
        favorite_genres=["pop"],
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    defaults.update(overrides)
    return UserProfile(**defaults)


# ---------------------------------------------------------------------------
# Recommender (existing tests — keep passing)
# ---------------------------------------------------------------------------

def test_recommend_returns_songs_sorted_by_score():
    user = make_user()
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = make_user()
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])

    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ---------------------------------------------------------------------------
# score_song — weighted scoring logic
# ---------------------------------------------------------------------------

def test_score_song_genre_match_adds_points():
    songs = make_songs()
    user = make_user(favorite_genres=["pop"])
    pop_score = score_song(songs[0], user)   # pop song
    lofi_score = score_song(songs[1], user)  # lofi song
    assert pop_score > lofi_score


def test_score_song_mood_match_adds_points():
    songs = make_songs()
    happy_user = make_user(favorite_mood="happy")
    chill_user = make_user(favorite_mood="chill")

    # Song 0 is happy — should score higher for happy_user
    assert score_song(songs[0], happy_user) > score_song(songs[0], chill_user)


def test_score_song_energy_proximity():
    songs = make_songs()
    # User wants high energy (0.9) — rock song (0.95) should beat lofi (0.4)
    user = make_user(favorite_genres=[], favorite_mood="", target_energy=0.9)
    assert score_song(songs[2], user) > score_song(songs[1], user)


def test_score_song_disliked_song_scores_very_low():
    songs = make_songs()
    user = make_user()
    user.disliked_song_ids.append(songs[0].id)
    assert score_song(songs[0], user) < 0


# ---------------------------------------------------------------------------
# collect_feedback
# ---------------------------------------------------------------------------

def test_collect_feedback_liked_adds_to_liked_ids():
    songs = make_songs()
    user = make_user()
    collect_feedback(user, songs[0], liked=True)
    assert songs[0].id in user.liked_song_ids
    assert songs[0].id not in user.disliked_song_ids


def test_collect_feedback_disliked_adds_to_disliked_ids():
    songs = make_songs()
    user = make_user()
    collect_feedback(user, songs[0], liked=False)
    assert songs[0].id in user.disliked_song_ids
    assert songs[0].id not in user.liked_song_ids


def test_collect_feedback_no_duplicates():
    songs = make_songs()
    user = make_user()
    collect_feedback(user, songs[0], liked=True)
    collect_feedback(user, songs[0], liked=True)
    assert user.liked_song_ids.count(songs[0].id) == 1


# ---------------------------------------------------------------------------
# refine_user_profile
# ---------------------------------------------------------------------------

def test_refine_updates_target_energy_from_liked_songs():
    songs = make_songs()
    user = make_user(target_energy=0.5)
    collect_feedback(user, songs[0], liked=True)   # energy 0.8
    refine_user_profile(user, songs)
    assert abs(user.target_energy - 0.8) < 0.01


def test_refine_updates_favorite_genres_from_liked_songs():
    songs = make_songs()
    user = make_user(favorite_genres=["rock"])
    collect_feedback(user, songs[1], liked=True)   # lofi song
    refine_user_profile(user, songs)
    assert "lofi" in user.favorite_genres


def test_refine_does_nothing_with_no_likes():
    songs = make_songs()
    user = make_user(target_energy=0.5)
    refine_user_profile(user, songs)   # no feedback given
    assert user.target_energy == 0.5   # unchanged


# ---------------------------------------------------------------------------
# get_popular_songs_by_genre (cold-start bootstrap)
# ---------------------------------------------------------------------------

def test_bootstrap_only_returns_songs_from_selected_genres():
    songs = make_songs()
    results = get_popular_songs_by_genre(songs, genres=["pop"])
    assert all(s.genre == "pop" for s in results)


def test_bootstrap_returns_at_most_k_songs():
    songs = make_songs()
    results = get_popular_songs_by_genre(songs, genres=["pop", "lofi", "rock"], k=2)
    assert len(results) <= 2


def test_bootstrap_returns_empty_for_unknown_genre():
    songs = make_songs()
    results = get_popular_songs_by_genre(songs, genres=["jazz"])
    assert results == []


# ---------------------------------------------------------------------------
# onboard_user
# ---------------------------------------------------------------------------

def test_onboard_user_sets_favorite_genres():
    user = onboard_user(["pop", "lofi"])
    assert user.favorite_genres == ["pop", "lofi"]


def test_onboard_user_starts_with_empty_feedback():
    user = onboard_user(["pop"])
    assert user.liked_song_ids == []
    assert user.disliked_song_ids == []
