# Housing Documentation in Discharge Summaries for Serious Mental Illness

This project detects whether clinicians document a patient's housing situation in hospital discharge
notes, using four NLP methods of increasing sophistication — from a regex keyword search to
a fine-tuned clinical transformer — applied to a cohort of 3,808 MIMIC-IV admissions for
serious mental illness (SMI).

<img width="980" height="357" alt="Screenshot 2026-08-10 at 5 45 43 PM" src="https://github.com/user-attachments/assets/9585aa37-2c14-405d-a139-924be0da8f22" />



## Research question

> **How consistently is housing actually mentioned in discharge summaries for patients
> hospitalized with serious mental illness — and do mention rates differ by race,
> insurance, or diagnosis?**

For patients with SMI, housing is not a side topic in discharge planning; it determines
whether the plan works at all. If housing is documented inconsistently — or inconsistently
*across patient groups* — then downstream research and care coordination built on those
notes inherit that gap. Measuring the housing documentation rate requires solving a housing detection
problem, which is what this project is about.

## Data

| Source | Role |
|---|---|
| **MIMIC-IV** (`admissions`, `patients`, `diagnoses_icd`) | ~546,000 admissions at Beth Israel Deaconess (2008–2019). Supplies demographics, insurance, discharge disposition, and ICD codes. |
| **MIMIC-IV-Note** | The free-text discharge summaries searched for housing mentions. |
| **MIMIC-III-Labeled-SDOH** | 1,800 hand-labeled sentences across six SDOH categories (200 `HOUSING`). Binarized to a housing/not-housing target — this is the **only labeled training data**. |

All MIMIC data requires PhysioNet credentialing and a data use agreement, so no data files
are committed. See [Reproducing](#reproducing) below.

**Cohort construction** (see [notebooks/milestone2.ipynb](notebooks/milestone2.ipynb)):
~546,000 admissions → 10,168 with an SMI **first-listed** ICD code (schizophrenia, bipolar,
severe MDD) → 9,580 after dropping transfers, against-advice discharges, and in-hospital
deaths → **3,808** with a matched discharge note.

## Approach

The core methodological problem is a **granularity mismatch**: the labeled data is single
sentences (~10–25 words), while inference targets are full discharge notes (median ~2,000
words). A classifier trained on the labeled data cannot be applied directly to the discharge notes.

The pipeline resolves this by splitting each note into narrative sentences before inference:

1. **Section split** on `Header:` delimiters, dropping non-narrative sections (labs, meds,
   physical exam, identifiers).
2. **Sentence split** on `.!?`, dropping fragments that are too short, mostly numeric,
   mostly uppercase, lab-like, or medication orders.
3. **Narrative-prose filter** — keep sentences with a housing keyword or a subject pronoun;
   drop problem-list enumerations (low stopword density, high comma density, 3+ med names).

This yields **228,213 sentences**, at the same granularity as the training data. Each classification model
makes a prediction on each sentence, then aggregates to the admission level by **max** (a note is flagged if any
sentence is flagged).

Four detection methods are compared end to end:

| Method | Representation | Classifier |
|---|---|---|
| **Keyword search** | 28-pattern regex | — |
| **TF-IDF + Random Forest** | unigrams + bigrams, 5k features | RF, `class_weight='balanced'`, grid-searched |
| **Word2Vec + MLP** | custom 100-d embeddings trained on the SMI corpus, mean-pooled | 2-hidden-layer MLP, oversampled, F1-tuned threshold |
| **Bio_ClinicalBERT** | contextual, fine-tuned | class-weighted cross-entropy, F1-tuned threshold |

## Results

**Detection quality** on the held-out labeled SDOH validation split:

| Method | Precision | Recall | F1 |
|---|---|---|---|
| Keyword search | 0.53 | 0.52 | 0.53 |
| TF-IDF + Random Forest | 1.00 | 0.80 | 0.89 |
| Word2Vec + MLP | 0.88 | 0.72 | 0.79 |
| **Bio_ClinicalBERT** | **0.97** | **0.97** | **0.97** |
| Bio_ClinicalBERT + synthetic augmentation | 0.97 | 0.96 | 0.97 |

**Housing-mention rate** on the 3,808-admission SMI cohort:

| Method | Notes flagged | % of cohort |
|---|---|---|
| Keyword search (28 patterns) | 3,551 | 93.3% |
| Keyword search (refined, 45 phrase patterns) | 1,063 | 27.9% |
| TF-IDF + Random Forest | 67 | 1.8% |
| Word2Vec + MLP | 2,334 | 61.3% |
| Bio_ClinicalBERT | 3,808 | 100.0% |

### What this shows

- **Context matters, and the keyword search cannot see it.** ClinicalBERT rejects **54%** of
  all keyword-positive sentences — cases like *"discharged home in stable condition"* or
  *"lives at home with family"*, where a housing word appears with no housing-instability
  meaning. The broad terms (`home`, `lives`, `house`, `housing`) drive most of the
  keyword search's 93% rate; the refined phrase-based list drops it to 28%.
- **The four methods barely agree.** Across all 228,213 sentences, only **3** were flagged
  positive by all four methods; 39% were flagged by exactly one. Detection rate is not a
  stable quantity — it is an artifact of how you measure it.
- **Aggregation amplifies the threshold.** ClinicalBERT is near-perfect at the sentence level
  (F1 0.97) yet flags **100%** of notes. Its F1-tuned threshold is 0.054, and taking the max
  over ~60 sentences per note means one borderline sentence flags the whole admission. This
  is a genuine limitation of max-aggregation, not evidence that every note documents housing —
  a note-level decision rule (e.g. count or confidence-weighted aggregation) is the natural
  next step.
- **Subgroup patterns hold across methods.** Housing mention rates are higher for Black and
  Hispanic patients than White patients, substantially higher for schizophrenia than for
  bipolar disorder or MDD, and higher for Medicare/Medicaid than private insurance. Where the
  methods agree on a subgroup gap, the gap is more likely real than a measurement artifact.

## Repository structure

```
notebooks/
  milestone2.ipynb                    Cohort construction, text cleaning, EDA, keyword baseline
  milestone3.ipynb                    Extended EDA, TF-IDF+RF and Word2Vec+MLP baselines
  milestone4.ipynb                    Full pipeline: all four methods, inference, subgroup analysis
  milestone4_keyword_filtered.ipynb   Variant restricting inference to keyword-matching sentences
  gcs_to_googledrive.ipynb            Utility: copy MIMIC files from a GCS bucket to Drive
docs/
  tfidf_explanation.md                Walkthrough of TF-IDF vectorization
reports/
  slides/                             Presentation decks (pdf + pptx)
scripts/
  build_milestone3_slides.py          Generates reports/slides/milestone3_presentation.pptx
```

Read [milestone4.ipynb](notebooks/milestone4.ipynb) first — it is the complete pipeline and
supersedes the earlier notebooks.

## Reproducing

The notebooks are written for **Google Colab with a GPU** (ClinicalBERT inference over
228k sentences takes ~5 min on a T4 versus ~3 hours on CPU) and fall back to local
execution automatically.

1. Obtain PhysioNet credentialing and download MIMIC-IV, MIMIC-IV-Note, and
   MIMIC-III-Labeled-SDOH.
2. Place the CSVs in `data/` (local) or `MyDrive/AC209b-project-data/` (Colab). The notebooks
   detect the runtime and set `DATA_DIR` accordingly.
3. Run [notebooks/milestone2.ipynb](notebooks/milestone2.ipynb) to build the cohort, then
   [notebooks/milestone4.ipynb](notebooks/milestone4.ipynb) for the full pipeline. Missing
   packages are pip-installed by the first cell; a global seed of 42 is set throughout.

Fine-tuned model weights, tuned thresholds, and BERT predictions are cached to Drive, so
reruns skip the expensive training and inference passes.

## Authors

Matlin Gilman and Brianna Grissom — Harvard AC209B / CS1090B, Project #63.
