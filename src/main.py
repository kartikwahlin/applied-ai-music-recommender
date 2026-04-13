"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    high_energy_pop   = {"genre": "pop",  "mood": "happy",   "energy": 0.85, "tempo_bpm": 125, "valence": 0.82, "acousticness": 0.15}
    chill_lofi_study  = {"genre": "lofi", "mood": "chill",   "energy": 0.38, "tempo_bpm": 78,  "valence": 0.58, "acousticness": 0.80}
    deep_intense_rock = {"genre": "rock", "mood": "intense", "energy": 0.92, "tempo_bpm": 155, "valence": 0.40, "acousticness": 0.08}
    dead_center = {"genre": "indie", "mood": "neutral", "energy": 0.50, "tempo_bpm": 100, "valence": 0.50, "acousticness": 0.50}
    ghost_genre = {"genre": "k-pop", "mood": "melancholic", "energy": 0.80, "tempo_bpm": 120, "valence": 0.85, "acousticness": 0.10}


    user_prefs = high_energy_pop   # swap this to test a different profile

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print()
    print("=" * 52)
    print("  Music Recommender — Top 5 Picks")
    print(f"  Profile: {user_prefs['genre']} · {user_prefs['mood']} · energy {user_prefs['energy']}")
    print("=" * 52)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print()
        print(f"  #{rank}  {song['title']}  —  {song['artist']}")
        print(f"       Genre: {song['genre']}  |  Mood: {song['mood']}  |  Energy: {song['energy']}")
        print(f"       Score: {score:.2f}")
        for reason in explanation.split(" | "):
            print(f"         • {reason}")

    print()
    print("=" * 52)
    print()


if __name__ == "__main__":
    main()
