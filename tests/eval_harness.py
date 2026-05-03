"""
Eval harness for the music recommender system.
Run from the project root: python tests/eval_harness.py
Prints a pass/fail summary for invariants, edge cases, and guardrails.
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from recommender import load_songs, recommend_songs, score_song, Song, Recommender, UserProfile

DATA_DIR = Path(__file__).parent.parent / "data"
SONGS_CSV = DATA_DIR / "songs.csv"

results = []


def check(name: str, passed: bool, detail: str = "") -> None:
    status = "PASS" if passed else "FAIL"
    results.append(passed)
    line = f"  [{status}] {name}"
    if detail:
        line += f" — {detail}"
    print(line)


# ---------------------------------------------------------------------------
# Load catalog
# ---------------------------------------------------------------------------
songs = load_songs(str(SONGS_CSV))

print("\nRunning eval harness...\n")

# ---------------------------------------------------------------------------
# 1. Invariants
# ---------------------------------------------------------------------------
print("Invariants")

# Results are always sorted descending by score
recs = recommend_songs({"genre": "pop", "mood": "happy", "energy": 0.8}, songs, k=5)
scores = [score for _, score, _ in recs]
check("Results are sorted descending by score", scores == sorted(scores, reverse=True))

# Genre match always adds points vs no match on identical prefs
base_prefs = {"energy": 0.5, "valence": 0.5, "acousticness": 0.5, "tempo_bpm": 100}
pop_song = next(s for s in songs if s["genre"] == "pop")
score_with_match, _ = score_song({**base_prefs, "genre": "pop"}, pop_song)
score_without_match, _ = score_song({**base_prefs, "genre": "rock"}, pop_song)
check("Genre match scores higher than genre mismatch", score_with_match > score_without_match)

# Mood match always adds points vs no match
score_with_mood, _ = score_song({**base_prefs, "mood": pop_song["mood"]}, pop_song)
score_without_mood, _ = score_song({**base_prefs, "mood": "angry"}, pop_song)
check("Mood match scores higher than mood mismatch", score_with_mood > score_without_mood)

# Scores are always non-negative
all_scores = [score_song(base_prefs, s)[0] for s in songs]
check("All scores are non-negative", all(s >= 0 for s in all_scores))

# Top result always has the highest score across the full catalog
recs_full = recommend_songs({"genre": "lofi", "mood": "chill", "energy": 0.4}, songs, k=len(songs))
top_score = recs_full[0][1]
check(
    "Top result has the highest score in the catalog",
    all(top_score >= s for _, s, _ in recs_full),
)

# ---------------------------------------------------------------------------
# 2. Edge cases
# ---------------------------------------------------------------------------
print("\nEdge cases")

# Unknown genre — should still return k results without crashing
try:
    recs = recommend_songs({"genre": "k-pop", "mood": "melancholic", "energy": 0.5}, songs, k=5)
    check("Unknown genre returns k results", len(recs) == 5)
except Exception as e:
    check("Unknown genre returns k results", False, str(e))

# k larger than catalog — should return all songs, not crash
try:
    recs = recommend_songs({"genre": "pop", "energy": 0.5}, songs, k=9999)
    check("k larger than catalog returns all songs", len(recs) == len(songs))
except Exception as e:
    check("k larger than catalog returns all songs", False, str(e))

# Prefs with no categorical fields — numeric-only profile
try:
    recs = recommend_songs({"energy": 0.5, "valence": 0.5}, songs, k=3)
    check("Numeric-only profile returns results", len(recs) == 3)
except Exception as e:
    check("Numeric-only profile returns results", False, str(e))

# Extreme energy values
try:
    recs_low = recommend_songs({"energy": 0.0}, songs, k=3)
    recs_high = recommend_songs({"energy": 1.0}, songs, k=3)
    check("Extreme energy values return results", len(recs_low) == 3 and len(recs_high) == 3)
except Exception as e:
    check("Extreme energy values return results", False, str(e))

# Empty catalog — should return empty list, not crash
try:
    recs = recommend_songs({"genre": "pop", "energy": 0.5}, [], k=5)
    check("Empty catalog returns empty list", recs == [])
except Exception as e:
    check("Empty catalog returns empty list", False, str(e))

# ---------------------------------------------------------------------------
# 3. Profile builder logic (derive_profile equivalent)
# ---------------------------------------------------------------------------
print("\nProfile builder")

from collections import Counter

def derive_profile(liked_songs: list) -> dict:
    if not liked_songs:
        return {"genre": "pop", "mood": "happy", "energy": 0.5,
                "tempo_bpm": 100.0, "valence": 0.5, "acousticness": 0.5}
    n = len(liked_songs)
    return {
        "genre": Counter(s["genre"] for s in liked_songs).most_common(1)[0][0],
        "mood": Counter(s["mood"] for s in liked_songs).most_common(1)[0][0],
        "energy": sum(s["energy"] for s in liked_songs) / n,
        "tempo_bpm": sum(s["tempo_bpm"] for s in liked_songs) / n,
        "valence": sum(s["valence"] for s in liked_songs) / n,
        "acousticness": sum(s["acousticness"] for s in liked_songs) / n,
    }

# Zero liked songs falls back to default
profile = derive_profile([])
check("Zero liked songs produces a valid fallback profile", profile["genre"] == "pop")

# Numeric values stay within [0, 1]
liked = [s for s in songs if s["genre"] in ("lofi", "pop")][:4]
profile = derive_profile(liked)
numeric_fields = ["energy", "valence", "acousticness"]
in_range = all(0.0 <= profile[f] <= 1.0 for f in numeric_fields)
check("Derived numeric fields are within [0, 1]", in_range)

# Plurality genre is correctly selected
lofi_songs = [s for s in songs if s["genre"] == "lofi"]
rock_songs = [s for s in songs if s["genre"] == "rock"][:1]
liked = lofi_songs + rock_songs
profile = derive_profile(liked)
check(
    "Plurality genre is selected correctly",
    profile["genre"] == "lofi",
    f"got '{profile['genre']}' from {len(lofi_songs)} lofi + {len(rock_songs)} rock",
)

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
passed = sum(results)
total = len(results)
avg_score = sum(
    score_song({"genre": "pop", "mood": "happy", "energy": 0.8}, s)[0] for s in songs
) / len(songs)

print(f"\n{'='*40}")
print(f"  {passed}/{total} tests passed | baseline avg score: {avg_score:.2f}")
print(f"{'='*40}\n")

sys.exit(0 if passed == total else 1)
