# Model Card: Music Recommender Simulation

## 1. Model Name

Songs & Vibes 1.0

---

## 2. Intended Use

Songs & Vibes is a content-based music recommender designed for classroom exploration. It suggests up to 5 songs from a small catalog based on a user's preferred genres, mood, energy level, and acoustic taste. It is not intended for production use — the catalog is tiny and the scoring logic is intentionally simple to make the system easy to understand and modify.

---

## 3. How the Model Works

Songs & Vibes uses a **weighted feature-matching** approach (content-based filtering). For each song in the catalog, it computes a score that reflects how well the song fits the user's taste profile:

- **Genre match** is weighted most heavily (adds 3 points) because genre is the strongest indicator of whether someone will enjoy a song.
- **Mood match** adds 2 points when the song's mood matches what the user wants to feel.
- **Energy proximity** rewards songs whose energy level is close to the user's target; the closer the match, the higher the bonus (up to 1 point).
- **Acoustic preference** adds 1 point if the user likes acoustic music and the song is acoustic, or if the user prefers produced/electric sounds and the song is not acoustic.
- **Explicit feedback** is the strongest override: a previously liked song gets +5, a disliked song gets −10, so it never surfaces again.

Songs are then ranked by score and the top k are returned.

The system also includes a **cold-start flow**: new users pick genres they like, see 5 popular songs from those genres (ranked by energy × danceability), rate each one, and then have their profile automatically refined from their feedback before personalized recommendations are generated.

---

## 4. Data

The catalog contains **22 songs** stored in `data/songs.csv`. Each song has the following features: id, title, artist, genre, mood, energy (0–1), tempo (BPM), valence (0–1), danceability (0–1), and acousticness (0–1).

Genres represented: **pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, country, edm, r&b, folk, metal**

Moods represented: **happy, chill, intense, relaxed, focused, moody, confident**

The catalog was expanded from 10 to 22 songs to improve recommendation diversity. All artists are fictional. The catalog still has no classical, latin, or reggae representation, and skews toward Western popular music styles.

---

## 5. Strengths

- Works well for users with clear genre preferences (e.g., lofi or pop), since genre carries the highest weight.
- The cold-start flow means even a brand-new user gets reasonable results before any history exists.
- Scoring is fully transparent — every point added to a song's score has a direct, human-readable reason.
- The `explain_recommendation` function surfaces exactly why each song was recommended, which mirrors what Pandora does with its Music Genome annotations.

---

## 6. Limitations and Bias

- **Small catalog**: With only 22 songs, diversity is limited — for niche genres (e.g., metal, country) there may only be 1–2 candidates, making it hard to return a meaningful top-5.
- **No collaborative filtering**: The system cannot learn from what other similar users liked, which is how most real recommenders improve over time.
- **Energy is the only continuous feature used in scoring**: Tempo, valence, and danceability are present in the data but not weighted in `score_song`, so two songs with very different feels can receive identical scores.
- **Genre bias**: Because genre adds 3 points and mood adds 2, a song in the right genre will almost always outrank a song in the wrong genre regardless of every other feature.
- **Acoustic preference is binary**: Users either like acoustic music or they don't — there is no spectrum, which flattens real taste.
- **Cold-start popularity proxy is rough**: Popularity is estimated as `energy × 0.6 + danceability × 0.4`, which biases bootstrap recommendations toward high-energy tracks and may alienate users who prefer calm music from the start.

---

## 7. Evaluation

The system was tested with several synthetic user profiles:

| Profile | Expected top results | Actual behavior |
| --- | --- | --- |
| Lofi chill fan, low energy, acoustic | Library Rain, Midnight Coding, Focus Flow | Correct — lofi songs ranked highest |
| Pop/rock fan, high energy, not acoustic | Gym Hero, Storm Runner, Sunrise City | Correct — pop and rock dominated |
| Jazz/ambient, relaxed mood | Coffee Shop Stories, Spacewalk Thoughts | Correct, though catalog is thin |
| Cold-start user who dislikes all bootstrap songs | Should surface unseen songs only | Dislike penalty (−10) correctly excludes them |

No numeric accuracy metric was used, but the score outputs were inspected manually and matched intuition in all test cases.

---

## 8. Future Work

- **Expand the catalog** to at least 100 songs so diversity in recommendations is meaningful.
- **Add collaborative filtering**: if two users liked the same 3 songs, recommend what the other liked next — this is how Spotify's "Discover Weekly" works.
- **Use more audio features in scoring**: valence and tempo are already in the data and could be weighted to distinguish an upbeat pop song from a sad one with the same genre label.
- **Soften the acoustic preference** from a binary flag to a continuous weight so users can prefer "somewhat acoustic" rather than just yes or no.
- **Add diversity constraints** so the top 5 results don't all come from the same genre.

---

## 9. Personal Reflection

Building Songs & Vibes made the mechanics of content-based filtering very concrete. The system works exactly as well as the features it knows about. If mood and genre are in the data, those drive the result; if lyrical theme or tempo range are not, the model is blind to them. That gap between "what we measured" and "what the user actually feels" is probably the most important limitation of any recommender, not just this one.

It was also surprising how much the weighting choices matter. Changing the genre weight from 3.0 to 1.0 completely reshuffled the rankings for mixed-genre users. Real platforms like Pandora spend enormous effort tuning exactly these weights, and this simulation made it clear why small changes in the scoring formula have an outsized effect on what people actually hear.
