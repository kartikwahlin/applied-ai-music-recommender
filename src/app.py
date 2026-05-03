import sys
import os
import json
import random
import logging
from pathlib import Path
from collections import Counter
from typing import Optional

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))
from recommender import load_songs, recommend_songs

# --- Paths ---
DATA_DIR = Path(__file__).parent.parent / "data"
SONGS_CSV = DATA_DIR / "songs.csv"
PROFILES_DIR = DATA_DIR / "profiles"
PROFILE_PATH = PROFILES_DIR / "profile.json"
LOG_PATH = Path(__file__).parent.parent / "recommender.log"

NUM_RATING_SONGS = 8

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


# --- Profile logic ---

def derive_profile(liked_songs: list) -> dict:
    if not liked_songs:
        logger.warning("No liked songs — falling back to default profile")
        return {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.5,
            "tempo_bpm": 100.0,
            "valence": 0.5,
            "acousticness": 0.5,
        }
    n = len(liked_songs)
    genre = Counter(s["genre"] for s in liked_songs).most_common(1)[0][0]
    mood = Counter(s["mood"] for s in liked_songs).most_common(1)[0][0]
    profile = {
        "genre": genre,
        "mood": mood,
        "energy": sum(s["energy"] for s in liked_songs) / n,
        "tempo_bpm": sum(s["tempo_bpm"] for s in liked_songs) / n,
        "valence": sum(s["valence"] for s in liked_songs) / n,
        "acousticness": sum(s["acousticness"] for s in liked_songs) / n,
    }
    logger.info("Profile derived from %d liked songs: genre=%s mood=%s", n, genre, mood)
    return profile


def save_profile(profile: dict) -> None:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)
    logger.info("Profile saved to %s", PROFILE_PATH)


def load_profile() -> Optional[dict]:
    if not PROFILE_PATH.exists():
        return None
    try:
        with open(PROFILE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        logger.error("Failed to load profile: %s", e)
        return None


# --- Session state ---

def init_session() -> None:
    if "all_songs" not in st.session_state:
        try:
            st.session_state.all_songs = load_songs(str(SONGS_CSV))
            logger.info("Loaded %d songs from catalog", len(st.session_state.all_songs))
        except (FileNotFoundError, OSError) as e:
            logger.error("Could not load songs CSV: %s", e)
            st.error(f"Could not load song catalog: {e}")
            st.stop()
    if "page" not in st.session_state:
        st.session_state.page = "builder"
    if "songs_to_rate" not in st.session_state:
        st.session_state.songs_to_rate = random.sample(
            st.session_state.all_songs, NUM_RATING_SONGS
        )
    if "current_idx" not in st.session_state:
        st.session_state.current_idx = 0
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}
    if "profile" not in st.session_state:
        st.session_state.profile = None


# --- Pages ---

def render_builder() -> None:
    st.title("Music Recommender")
    st.subheader("Rate some songs to build your profile")

    songs_to_rate = st.session_state.songs_to_rate
    idx = st.session_state.current_idx

    if idx >= len(songs_to_rate):
        liked = [
            s for s in songs_to_rate
            if st.session_state.ratings.get(s["id"]) == "like"
        ]
        profile = derive_profile(liked)
        save_profile(profile)
        st.session_state.profile = profile

        n = len(liked)
        if n == 0:
            st.warning("You didn't like any songs — using a default profile.")
        else:
            st.success(f"Profile built from {n} liked song{'s' if n != 1 else ''}.")

        if st.button("See Your Recommendations →", type="primary"):
            st.session_state.page = "recommendations"
            st.rerun()
        return

    st.caption(f"Song {idx + 1} of {len(songs_to_rate)}")
    st.progress(idx / len(songs_to_rate))

    song = songs_to_rate[idx]

    with st.container(border=True):
        st.markdown(f"### {song['title']}")
        st.markdown(f"*{song['artist']}*")

        col1, col2 = st.columns(2)
        col1.metric("Genre", song["genre"].title())
        col2.metric("Mood", song["mood"].title())

        col3, col4 = st.columns(2)
        col3.metric("Energy", f"{song['energy']:.0%}")
        col4.metric("Tempo", f"{int(song['tempo_bpm'])} BPM")

    col_like, col_dislike = st.columns(2)
    if col_like.button("👍  Like", use_container_width=True, type="primary"):
        st.session_state.ratings[song["id"]] = "like"
        st.session_state.current_idx += 1
        logger.info("User rated song %d ('%s') as like", song["id"], song["title"])
        st.rerun()
    if col_dislike.button("👎  Dislike", use_container_width=True):
        st.session_state.ratings[song["id"]] = "dislike"
        st.session_state.current_idx += 1
        logger.info("User rated song %d ('%s') as dislike", song["id"], song["title"])
        st.rerun()


def render_recommendations() -> None:
    st.title("Your Recommendations")

    profile = st.session_state.profile or load_profile()

    if profile is None:
        st.error("No profile found. Please build your profile first.")
        if st.button("Build Profile"):
            st.session_state.page = "builder"
            st.rerun()
        return

    with st.expander("Your taste profile"):
        col1, col2 = st.columns(2)
        col1.metric("Top Genre", profile["genre"].title())
        col1.metric("Top Mood", profile["mood"].title())
        col2.metric("Energy", f"{profile['energy']:.0%}")
        col2.metric("Acousticness", f"{profile['acousticness']:.0%}")

    songs = st.session_state.all_songs
    recommendations = recommend_songs(profile, songs, k=5)
    logger.info(
        "Recommendations generated for profile genre=%s mood=%s",
        profile["genre"], profile["mood"],
    )

    st.markdown("### Top Picks For You")

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        with st.container(border=True):
            col_title, col_score = st.columns([4, 1])
            col_title.markdown(f"**#{rank} {song['title']}** — {song['artist']}")
            col_score.metric("Score", f"{score:.2f}")

            col1, col2, col3 = st.columns(3)
            col1.caption(f"Genre: {song['genre'].title()}")
            col2.caption(f"Mood: {song['mood'].title()}")
            col3.caption(f"Energy: {song['energy']:.0%}")

            with st.expander("Why this song?"):
                for reason in explanation.split(" | "):
                    st.caption(f"• {reason}")

    st.divider()
    if st.button("Start Over", type="secondary"):
        for key in ["songs_to_rate", "current_idx", "ratings", "profile"]:
            st.session_state.pop(key, None)
        st.session_state.page = "builder"
        logger.info("User started over")
        st.rerun()


# --- Entry point ---

def main() -> None:
    st.set_page_config(
        page_title="Music Recommender",
        page_icon="🎵",
        layout="centered",
    )
    init_session()

    if st.session_state.page == "builder":
        render_builder()
    elif st.session_state.page == "recommendations":
        render_recommendations()


if __name__ == "__main__":
    main()
