# Model Card: Music Recommender

## Model Name
genreMatcher

---

## Intended Use
The system takes user preferences and suggests songs from a catalog that the user is likely to enjoy. It assumes the user can be represented by a genre, mood, and a set of numeric audio features (energy, tempo, valence, acousticness). This is a classroom exploration of how content-based filtering works — a real system would derive preferences from listening history rather than manual input.

---

## How the Model Works
Each song in the catalog is compared to the user's preference profile using a weighted scoring system. Genre and mood are checked for exact matches and add a fixed bonus if they align. Numeric features like energy, tempo, and acousticness are compared by proximity; the closer a song's value is to the user's preference, the higher it scores. All scores are summed and the top results are returned. There is no learning involved; the same input always produces the same output.

---

## Data
The catalog contains 20 songs spanning a wide range of genres including pop, lofi, rock, jazz, classical, hip-hop, EDM, country, R&B, blues, folk, reggae, and soul. Moods include happy, chill, intense, focused, peaceful, melancholic, and more. There is a slight concentration in pop and lofi. 

---

## Strengths
When a user's genre and mood preferences align with songs in the catalog, recommendations are intuitive and well-matched. The system is fully transparent and every score can be explained reason by reason. Results are deterministic, so there are no surprises from run to run.

---

## Limitations and Bias

**What are the limitations or biases in your system?**

- The system heavily prioritizes genre and mood matches (+2.0 and +1.5 respectively), which can overshadow numeric feature similarity. A song in the wrong genre with a perfect energy match will lose to an on-genre song with mismatched energy.
- Tempo scoring is uncapped on the low end — a very large BPM difference can produce a negative contribution, which could in theory drag a score below zero if other features are weak.
- The catalog underrepresents some genres entirely (no k-pop, no latin, no metal subgenres beyond one entry), so users with those preferences will always receive cross-genre recommendations regardless of their input.
- The profile builder derives preferences by averaging liked songs, which makes it sensitive to outliers — one very high-energy like inflates the target energy for all recommendations.
- This model is only tested for these 20 songs, and other issues with new data may arise.

---

## Could Your AI Be Misused, and How Would You Prevent It?

The system is low-risk by nature because it recommends songs and does nothing else. It doesn't include API calls, but it might be exploited if part of a larger song-streaming service to prioritize an artist.

---

## Evaluation

**What surprised you while testing your AI's reliability?**

The eval harness passed all 13 tests on the first run, which was not expected. The more interesting finding was that the "dead center" profile (energy=0.5, no genre or mood) produced a surprisingly diverse list — blues, lofi, country, and soul all appearing together — because energy proximity became the dominant factor when categorical bonuses were absent. This revealed that the genre/mood weights are what create the appearance of a "smart" recommender; without them, it reduces to a nearest-neighbor search on energy.

I also tested rock versus lofi profiles and confirmed that rock recommendations were consistently high-energy and lofi recommendations were consistently below 0.5 energy, which matched intuition and validated the scoring weights.

---

## AI Collaboration

**Helpful suggestion:** When designing the eval harness, Claude reframed what reliability testing means for a deterministic system — shifting focus from "did it get the right answer" to "do structural guarantees hold under stress." This was a more honest and useful framing than the original plan of just checking expected outputs.

**Flawed suggestion:** Claude initially tried to develop an entirely CLI-based tool, which, although effective for this version of the program, would have limited user clarity and potential improvements to the frontend.

---

## Reflection

This project clarified how recommender systems actually work at a mechanical level, and filled in the part that the original music matcher missed. I learned a good deal about how these algorithms figure out who their users are, and I understand why youTube asks you to search videos up when you start with a fresh profile - it has no user data to base its recommendations off of.