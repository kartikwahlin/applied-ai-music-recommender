# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

With accurate mood and genre tags, it will match them properly.
Outliers are very rare, since it doesn't do anything after deciding score.
---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

Some of the issues of this recommender include:
- BPM is uncapped and can add infinite positive or negative value in odd cases
- It heavily prioritizes genre and mood
- It doesn't do anything to make sure it's avoiding repeat songs. many phonk artists like to publish slowed version of their songs.



---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested rock versus lo-fi, and it seemed like rock was always high-energy, and lo-fi was always below 0.5. This makes sense, since lo-fi is entirely about being low energy, and rock is usually about being higher energy.
I generally paid attention to energy and acousticness, since the genre and mood were usually matches and had few outliers.
The 'dead center' profile gave a wide variety of genres, since the strongest metrick seemed to be energy proximity. It ended up with blues, lo-fi, country, and soul songs all in the same list.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps 

This project really cleared up recommender systems for me. I learned about how to run python code from the terminal when claude used the -m flag, and it taught me a bit about easily making testcases and writing apt docstrings. Now I know why spotify refuses to get off of certain genres at times.
