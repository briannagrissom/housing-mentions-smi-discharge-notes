# How TF-IDF Vectorization Works

**TF-IDF** stands for **Term Frequency-Inverse Document Frequency**. It's a fundamental statistical technique used in Natural Language Processing (NLP) to convert raw text into a numerical format (a matrix) that machine learning models can process, while simultaneously highlighting the most meaningful words in a text.

It works by scoring words based on two main principles:

## 1. Term Frequency (TF)
This answers the question: *How frequently does a word appear in a single document/sentence?*
- If the word "homeless" appears 5 times in a discharge note, its TF is high for that specific note.
- **Formula**: `(Number of times term T appears in a document) / (Total number of words in that document)`

*The limitation of only using TF:* Words like "the," "patient," or "is" will have incredibly high scores simply because they are common grammatical fillers, not because they carry clinical meaning.

## 2. Inverse Document Frequency (IDF)
This answers the question: *How rare is the word across ALL the documents in the entire dataset?*
- A word that appears in almost every discharge note (like "blood" or "patient") will have a very low IDF score. 
- A word that appears in only a few specific notes (like "encampment" or "evicted") will get a **massive boost** to its IDF score because it is rare and distinctive.
- **Formula**: `log(Total number of documents / Number of documents containing term T)`

## The Final Score = TF $\\times$ IDF
To get the final representation for a word in a specific document, you multiply the two scores together:
- **Low Score**: A word gets a low score if it appears rarely in the specific document, or if it appears frequently across *all* documents (e.g., "the", "and", "doctor").
- **High Score**: A word gets a high score if it appears frequently in a *specific* document, but rarely in the *entire dataset* (e.g., "unsheltered", "haloperidol"). 

---

## How It Maps to a Vector (The Document-Term Matrix)

To map the TF-IDF scores for individual words into a single uniform vector for an entire discharge note, the algorithm relies on building a **fixed vocabulary** and creating a **Document-Term Matrix**.

### Step 1: Building the Global Vocabulary (The "Features")
First, the vectorizer scans the entire dataset to find every unique word (and bigrams, if `ngram_range=(1,2)`). 
- It creates a master "Vocabulary List" giving every unique term a specific, fixed position (an index).
- For example, if we set `max_features=5`, our vocabulary map might look like this:
  - Index 0: "blood"
  - Index 1: "homeless"
  - Index 2: "patient"
  - Index 3: "shelter"
  - Index 4: "stable"

This means **every single note** will be represented mathematically as a vector of length 5: `[_, _, _, _, _]`, where position 1 always represents the concept of "homeless".

### Step 2: Creating the Vector for a Single Note
When the vectorizer analyzes a specific note, it calculates the TF-IDF score for the words actually present and places them into their assigned slots. Words missing from the note get a score of `0.0`.

**Example Note A**: *"The patient is homeless and looking for a shelter."*
- "blood": 0 times (Score: `0.00`)
- "homeless": 1 time (TF-IDF Score: `0.85`)
- "patient": 1 time (TF-IDF Score: `0.15` — *low score due to IDF penalty*)
- "shelter": 1 time (TF-IDF Score: `0.78`)
- "stable": 0 times (Score: `0.00`)

**Vector A**: `[0.00, 0.85, 0.15, 0.78, 0.00]`

**Example Note B**: *"The patient is stable and has stable housing."*
- "stable": 2 times (TF-IDF Score: `0.65`)
- *others*: 0 times

**Vector B**: `[0.00, 0.00, 0.15, 0.00, 0.65]`

### Step 3: The Final Document-Term Matrix
When applied to your entire SMI Cohort (3,808 notes) with `max_features=5000` set, the TF-IDF vectorizer outputs a massive 2D matrix that is `3808 rows` by `5000 columns`. 

Each row represents an entire discharge note, and each column corresponds to a specific word's TF-IDF score. Because no single discharge note contains all 5,000 top words, the resulting vectors are mostly zeros—this creates a **Sparse Matrix**, which is computationally efficient for algorithms like Random Forests to process!
