import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

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
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Returns a (score, reasons) tuple so callers can both rank and explain.

    Weights:
      genre match   +2.0  (strongest explicit preference)
      mood match    +1.5  (session intent)
      energy        ×1.5  (numeric proximity, 0–1 range)
      acousticness  ×1.0  (numeric proximity, 0–1 range)
      valence       ×0.75 (numeric proximity, 0–1 range)
      tempo         ×0.5  (numeric proximity, normalised over 200 BPM)
    """
    score = 0.0
    reasons = []

    # --- Categorical matches ---
    if user_prefs.get("genre") and song["genre"] == user_prefs["genre"]:
        score += 2.0
        reasons.append("genre match (+2.0)")

    if user_prefs.get("mood") and song["mood"] == user_prefs["mood"]:
        score += 1.5
        reasons.append("mood match (+1.5)")

    # --- Numeric proximity scores ---
    if "energy" in user_prefs:
        pts = (1 - abs(user_prefs["energy"] - song["energy"])) * 1.5
        score += pts
        reasons.append(f"energy proximity ({pts:+.2f})")

    if "acousticness" in user_prefs:
        pts = (1 - abs(user_prefs["acousticness"] - song["acousticness"])) * 1.0
        score += pts
        reasons.append(f"acousticness proximity ({pts:+.2f})")

    if "valence" in user_prefs:
        pts = (1 - abs(user_prefs["valence"] - song["valence"])) * 0.75
        score += pts
        reasons.append(f"valence proximity ({pts:+.2f})")

    if "tempo_bpm" in user_prefs:
        pts = (1 - abs(user_prefs["tempo_bpm"] - song["tempo_bpm"]) / 200) * 0.5
        score += pts
        reasons.append(f"tempo proximity ({pts:+.2f})")

    return score, reasons


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        user_prefs = {
            "genre":      user.favorite_genre,
            "mood":       user.favorite_mood,
            "energy":     user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }
        scored = []
        for song in self.songs:
            song_dict = {
                "genre": song.genre, "mood": song.mood,
                "energy": song.energy, "tempo_bpm": song.tempo_bpm,
                "valence": song.valence, "acousticness": song.acousticness,
            }
            score, _ = score_song(user_prefs, song_dict)
            scored.append((score, song))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        user_prefs = {
            "genre":      user.favorite_genre,
            "mood":       user.favorite_mood,
            "energy":     user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }
        song_dict = {
            "genre": song.genre, "mood": song.mood,
            "energy": song.energy, "tempo_bpm": song.tempo_bpm,
            "valence": song.valence, "acousticness": song.acousticness,
        }
        _, reasons = score_song(user_prefs, song_dict)
        return " | ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = " | ".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
