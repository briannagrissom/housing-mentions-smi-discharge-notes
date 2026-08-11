"""Build milestone3_presentation.pptx matching the MS2 theme."""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN

# ---- Theme --------------------------------------------------------------
TEAL   = RGBColor(0x0B, 0x3B, 0x44)
RUST   = RGBColor(0xC2, 0x55, 0x3D)
BEIGE  = RGBColor(0xC9, 0xBE, 0xA3)
CREAM  = RGBColor(0xF6, 0xF1, 0xE6)
GRAY   = RGBColor(0x55, 0x55, 0x55)
BLACK  = RGBColor(0x1A, 0x1A, 0x1A)
WHITE  = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT  = RGBColor(0xF2, 0xED, 0xE0)  # very light cream for figure placeholders

FONT_SERIF = "Georgia"
FONT_SANS  = "Calibri"

TOTAL_SLIDES = 14
FOOTER_TEXT  = "Housing Documentation in SMI Discharge Summaries"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)

blank_layout = prs.slide_layouts[6]  # fully blank


# ---- helpers ------------------------------------------------------------
def add_rect(slide, left, top, width, height, fill, line=None):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(left), Inches(top),
                                   Inches(width), Inches(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
    shape.shadow.inherit = False
    return shape


def add_text(slide, left, top, width, height, runs, align=PP_ALIGN.LEFT, anchor="t"):
    """runs = list of dicts with keys: text, font, size, bold, color, (space_after)."""
    tb = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = 0
    tf.margin_top = tf.margin_bottom = 0
    if anchor == "m":
        from pptx.enum.text import MSO_ANCHOR
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE

    first = True
    for run_spec in runs:
        if run_spec.get("newline") and not first:
            p = tf.add_paragraph()
        elif first:
            p = tf.paragraphs[0]
            first = False
        else:
            # Same paragraph, add a run
            p = tf.paragraphs[-1]
        p.alignment = run_spec.get("align", align)
        if "space_after" in run_spec:
            p.space_after = Pt(run_spec["space_after"])
        if run_spec.get("text") is None:
            continue
        r = p.add_run()
        r.text = run_spec["text"]
        r.font.name = run_spec.get("font", FONT_SANS)
        r.font.size = Pt(run_spec.get("size", 12))
        r.font.bold = run_spec.get("bold", False)
        color = run_spec.get("color", BLACK)
        r.font.color.rgb = color
    return tb


def add_chrome(slide, section_label, page_num):
    """Left sidebar, section label, footer line, footer text, page number."""
    # Left sidebar
    add_rect(slide, 0.0, 0.0, 0.32, 7.5, TEAL)
    # Section label (top right)
    add_text(slide, 7.50, 0.45, 5.30, 0.35,
             [{"text": section_label, "font": FONT_SANS, "size": 10, "bold": True, "color": RUST}])
    # Footer divider
    add_rect(slide, 0.70, 7.00, 12.00, 0.01, BEIGE)
    # Footer text
    add_text(slide, 0.70, 7.08, 8.00, 0.30,
             [{"text": FOOTER_TEXT, "font": FONT_SANS, "size": 9, "color": GRAY}])
    # Page number
    add_text(slide, 11.50, 7.08, 1.20, 0.19,
             [{"text": f"{page_num:02d} / {TOTAL_SLIDES}",
               "font": FONT_SANS, "size": 9, "bold": True, "color": TEAL}],
             align=PP_ALIGN.RIGHT)


def add_title(slide, title):
    add_text(slide, 0.70, 0.95, 12.20, 0.95,
             [{"text": title, "font": FONT_SERIF, "size": 36, "bold": True, "color": TEAL}])
    # Rust underline
    add_rect(slide, 0.72, 1.78, 0.60, 0.06, RUST)


def add_eyebrow(slide, left, top, text, color=RUST):
    """Small uppercase Calibri label like 'WHY IT MATTERS'."""
    add_text(slide, left, top, 6.00, 0.30,
             [{"text": text, "font": FONT_SANS, "size": 10, "bold": True, "color": color}])


def add_bullets(slide, left, top, width, height, items, size=14, color=BLACK):
    """Bullet list with rust ▪ markers."""
    runs = []
    for i, item in enumerate(items):
        if i > 0:
            runs.append({"newline": True})
        runs.append({"text": "▪  ", "font": FONT_SANS, "size": size,
                     "bold": True, "color": TEAL, "space_after": 6})
        runs.append({"text": item, "font": FONT_SANS, "size": size, "color": color})
    return add_text(slide, left, top, width, height, runs)


def add_big_stat(slide, left, top_stat, width, stat, label, desc=None,
                 stat_size=44, stat_color=TEAL):
    """Big number + small label + optional description."""
    add_text(slide, left, top_stat, width, 0.90,
             [{"text": stat, "font": FONT_SERIF, "size": stat_size,
               "bold": True, "color": stat_color}])
    add_text(slide, left, top_stat + stat_size * 0.02 + 0.75, width, 0.30,
             [{"text": label, "font": FONT_SANS, "size": 10, "bold": True, "color": RUST}])
    if desc:
        add_text(slide, left, top_stat + stat_size * 0.02 + 1.03, width, 0.50,
                 [{"text": desc, "font": FONT_SANS, "size": 11, "color": GRAY}])


def add_figure_placeholder(slide, left, top, width, height, caption):
    """Light beige card with caption text marking where a figure goes."""
    add_rect(slide, left, top, width, height, WHITE, line=BEIGE)
    add_rect(slide, left + 0.08, top + 0.08, width - 0.16, height - 0.16, LIGHT)
    add_text(slide, left, top + height / 2 - 0.30, width, 0.30,
             [{"text": "[ FIGURE PLACEHOLDER ]", "font": FONT_SANS, "size": 11,
               "bold": True, "color": RUST, "align": PP_ALIGN.CENTER}],
             align=PP_ALIGN.CENTER)
    add_text(slide, left, top + height / 2 + 0.05, width, 0.50,
             [{"text": caption, "font": FONT_SANS, "size": 11,
               "color": GRAY, "align": PP_ALIGN.CENTER}],
             align=PP_ALIGN.CENTER)


# ========================================================================
# SLIDE 1 — Title
# ========================================================================
s = prs.slides.add_slide(blank_layout)
# Full teal background
add_rect(s, 0.0, 0.0, 13.333, 7.5, TEAL)
# Cream accent strip
add_rect(s, 0.0, 6.5, 13.333, 0.04, BEIGE)

# Top eyebrow
add_text(s, 1.0, 1.0, 11.3, 0.40,
         [{"text": "AC209B   ·   MILESTONE 3", "font": FONT_SANS, "size": 11,
           "bold": True, "color": BEIGE}])

# Main title
add_text(s, 1.0, 1.70, 11.3, 1.30,
         [{"text": "Does anyone write down", "font": FONT_SERIF, "size": 54,
           "bold": True, "color": CREAM}])
add_text(s, 1.0, 2.60, 11.3, 1.30,
         [{"text": "where they go home to?", "font": FONT_SERIF, "size": 54,
           "bold": True, "color": CREAM}])

# Rust underline
add_rect(s, 1.0, 3.85, 0.80, 0.08, RUST)

# Subtitle
add_text(s, 1.0, 4.15, 11.3, 0.60,
         [{"text": "Baseline modeling & inference on the SMI cohort",
           "font": FONT_SERIF, "size": 20, "color": CREAM}])

# Footer line
add_rect(s, 1.0, 5.60, 11.3, 0.01, BEIGE)

# Project & team
add_text(s, 1.0, 5.85, 5.5, 0.30,
         [{"text": "PROJECT", "font": FONT_SANS, "size": 10, "bold": True, "color": BEIGE}])
add_text(s, 1.0, 6.10, 5.5, 0.40,
         [{"text": "#63   ·   Baseline Models & Cohort Inference",
           "font": FONT_SERIF, "size": 16, "color": CREAM}])

add_text(s, 7.0, 5.85, 5.5, 0.30,
         [{"text": "TEAM", "font": FONT_SANS, "size": 10, "bold": True, "color": BEIGE}])
add_text(s, 7.0, 6.10, 5.5, 0.40,
         [{"text": "Matlin Gilman   ·   Brianna Grissom",
           "font": FONT_SERIF, "size": 16, "color": CREAM}])


# ========================================================================
# SLIDE 2 — Research Question
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "RESEARCH QUESTION", 2)
add_title(s, "Does anyone write down where they go home to?")

# Left column
add_eyebrow(s, 0.70, 2.30, "RESEARCH QUESTION")
add_text(s, 0.70, 2.65, 6.20, 2.20,
         [{"text": "How consistently is housing mentioned in "
                   "discharge summaries for patients hospitalized "
                   "with serious mental illness?",
           "font": FONT_SERIF, "size": 22, "bold": True, "color": TEAL}])

# Vertical divider
add_rect(s, 7.20, 2.30, 0.02, 4.50, BEIGE)

# Right column
add_eyebrow(s, 7.50, 2.30, "WHERE MS3 PICKS UP")
add_bullets(s, 7.50, 2.65, 5.30, 4.00,
            ["MS2 relied on a 23-keyword regex — caught only ~39% of real mentions",
             "MS3: train sentence-level classifiers on MIMIC-III-SDOH labels",
             "Apply each baseline to the MIMIC-IV SMI cohort (3,808 discharge notes)",
             "Pick the most trustworthy baseline before scaling to ClinicalBERT"],
            size=14)


# ========================================================================
# SLIDE 3 — MIMIC-III-SDOH Dataset
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "TRAINING DATA", 3)
add_title(s, "A labeled sentence dataset to train our baselines")

# Left: description card
add_eyebrow(s, 0.70, 2.30, "MIMIC-III-SDOH")
add_text(s, 0.70, 2.65, 7.80, 0.60,
         [{"text": "A labeled sentence dataset — ready-made training signal",
           "font": FONT_SERIF, "size": 20, "bold": True, "color": TEAL}])

add_eyebrow(s, 0.70, 3.50, "WHAT IT IS", color=RUST)
add_text(s, 0.70, 3.80, 7.80, 0.85,
         [{"text": "Hand-labeled clinical sentences from the MIMIC-III release, "
                   "tagged for social determinants of health (housing, food, "
                   "substance use, etc.).",
           "font": FONT_SANS, "size": 13, "color": BLACK}])

add_eyebrow(s, 0.70, 4.85, "WHY WE USE IT")
add_bullets(s, 0.70, 5.15, 7.80, 1.60,
            ["No hand-labeling needed — ground truth already validated",
             "Each sentence has a clean housing / non-housing label",
             "Split 80 / 20 stratified: 1,440 train · 360 val"],
            size=12)

# Right: big stats
add_big_stat(s, 9.20, 2.30, 3.80, "1,800", "LABELED SENTENCES",
             "across all SDOH categories")
add_big_stat(s, 9.20, 3.80, 3.80, "11.1%", "HOUSING (positive)",
             "200 sentences mention housing", stat_color=RUST)
add_big_stat(s, 9.20, 5.30, 3.80, "88.9%", "NON-HOUSING",
             "class imbalance we must handle")


# ========================================================================
# SLIDE 4 — Baseline 1: Keyword Search
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "BASELINE 1", 4)
add_title(s, "Start with the simplest thing that could work")

# Left: figure placeholder
add_figure_placeholder(s, 0.70, 2.20, 8.20, 3.80,
                       "Keyword fire-rates — only 9 of 23 terms trigger; "
                       "`homeless`, `street`, `shelter` dominate")

# Right: stats
add_big_stat(s, 9.20, 2.20, 3.80, "0.74", "PRECISION")
add_big_stat(s, 9.20, 3.25, 3.80, "0.39", "RECALL", stat_color=RUST)
add_big_stat(s, 9.20, 4.30, 3.80, "0.51", "F1 SCORE")

# Bottom teal banner
add_rect(s, 0.70, 6.15, 12.00, 0.80, TEAL)
add_text(s, 0.95, 6.32, 11.50, 0.50,
         [{"text": "Intuitive and transparent — zero training required. "
                   "High precision, but it misses 6 of 10 real mentions "
                   "because clinicians paraphrase.",
           "font": FONT_SERIF, "size": 14, "color": CREAM}])


# ========================================================================
# SLIDE 5 — Baseline 2: TF-IDF + Random Forest
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "BASELINE 2", 5)
add_title(s, "Let the model learn the phrases we didn't list")

# Left: description
add_eyebrow(s, 0.70, 2.30, "WHY THIS BASELINE")
add_bullets(s, 0.70, 2.65, 7.80, 1.40,
            ["Simple, interpretable way to turn text into vectors",
             "Random Forest captures non-linear n-gram interactions",
             "Sets a lower bound on what a lexical model can achieve"],
            size=13)

add_eyebrow(s, 0.70, 4.15, "FEATURES & TRAINING")
add_bullets(s, 0.70, 4.45, 7.80, 1.40,
            ["TF-IDF: unigrams + bigrams, 5k features, English stopwords",
             "Random Forest with class_weight='balanced' + GridSearchCV",
             "Trained & validated on MIMIC-III-SDOH (not MIMIC-IV)"],
            size=13)

# Context reminder banner
add_rect(s, 0.70, 6.00, 8.20, 0.50, CREAM)
add_text(s, 0.90, 6.09, 7.80, 0.35,
         [{"text": "Metrics below are on the MIMIC-III validation split. "
                   "Inference on MIMIC-IV comes later.",
           "font": FONT_SANS, "size": 11, "bold": True, "color": TEAL}])

# Right: stats
add_eyebrow(s, 9.20, 2.30, "MIMIC-III  ·  VALIDATION")
add_big_stat(s, 9.20, 2.65, 3.80, "1.00", "PRECISION")
add_big_stat(s, 9.20, 3.70, 3.80, "0.80", "RECALL")
add_big_stat(s, 9.20, 4.75, 3.80, "0.89", "F1 SCORE", stat_color=RUST)

# Bottom teal banner
add_rect(s, 0.70, 6.65, 12.00, 0.30, TEAL)
add_text(s, 0.95, 6.67, 11.50, 0.30,
         [{"text": "Zero false positives on the 360-sentence held-out set — "
                   "beats the keyword recall target by a wide margin.",
           "font": FONT_SERIF, "size": 12, "color": CREAM}])


# ========================================================================
# SLIDE 6 — Baseline 3: Word2Vec + MLP
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "BASELINE 3", 6)
add_title(s, "Move from word-matching to word-meaning")

# Left: description
add_eyebrow(s, 0.70, 2.30, "WHY THIS BASELINE")
add_bullets(s, 0.70, 2.65, 7.80, 1.40,
            ["TF-IDF counts words; Word2Vec learns meaning",
             "`unhoused`, `shelter`, `homeless` land near each other in vector space",
             "Simplest neural baseline — stepping-stone to ClinicalBERT"],
            size=13)

add_eyebrow(s, 0.70, 4.15, "FEATURES & TRAINING")
add_bullets(s, 0.70, 4.45, 7.80, 1.60,
            ["Word2Vec (100-dim, window 5) trained on the MIMIC-IV SMI corpus — used later for inference",
             "Sentence vector = mean of its word embeddings",
             "MLP classifier (100 → 50, early stopping); trained & validated on MIMIC-III-SDOH",
             "Decision threshold swept on validation, best F1 at 0.855"],
            size=12)

# Context reminder banner
add_rect(s, 0.70, 6.25, 8.20, 0.45, CREAM)
add_text(s, 0.90, 6.32, 7.80, 0.30,
         [{"text": "Metrics are on the MIMIC-III validation split. "
                   "MIMIC-IV inference comes later.",
           "font": FONT_SANS, "size": 11, "bold": True, "color": TEAL}])

# Right: stats — tuned threshold
add_eyebrow(s, 9.20, 2.30, "MIMIC-III  ·  TUNED THRESHOLD 0.855")
add_big_stat(s, 9.20, 2.65, 3.80, "0.94", "PRECISION")
add_big_stat(s, 9.20, 3.70, 3.80, "0.75", "RECALL")
add_big_stat(s, 9.20, 4.75, 3.80, "0.833", "F1 SCORE", stat_color=RUST)


# ========================================================================
# SLIDE 7 — Model Comparison
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "VALIDATION", 7)
add_title(s, "How the three baselines compare")

# Table area
table_left = 0.70
table_top = 2.30
table_w = 12.00
row_h = 0.70
header_h = 0.60

# Header row
add_rect(s, table_left, table_top, table_w, header_h, TEAL)
headers = [("MODEL", 4.50), ("PRECISION", 2.50), ("RECALL", 2.50), ("F1", 2.50)]
x = table_left
for i, (h, w) in enumerate(headers):
    align = PP_ALIGN.LEFT if i == 0 else PP_ALIGN.CENTER
    add_text(s, x + 0.25, table_top + 0.15, w - 0.3, header_h,
             [{"text": h, "font": FONT_SANS, "size": 12, "bold": True, "color": CREAM}],
             align=align)
    x += w

# Data rows
rows = [
    ("Keyword search",         "0.74",  "0.39",  "0.51",  False),
    ("TF-IDF + Random Forest", "1.00",  "0.80",  "0.89",  True),   # winner
    ("Word2Vec + MLP (tuned)", "0.94",  "0.75",  "0.833", False),
]
y = table_top + header_h
for i, (model, p, r, f, win) in enumerate(rows):
    fill = LIGHT if win else WHITE
    add_rect(s, table_left, y, table_w, row_h, fill, line=BEIGE)
    xx = table_left
    vals = [(model, 4.50, PP_ALIGN.LEFT, FONT_SERIF, 16, win, TEAL),
            (p,     2.50, PP_ALIGN.CENTER, FONT_SERIF, 18, win, RUST if win else TEAL),
            (r,     2.50, PP_ALIGN.CENTER, FONT_SERIF, 18, False, TEAL),
            (f,     2.50, PP_ALIGN.CENTER, FONT_SERIF, 18, win, RUST if win else TEAL)]
    for v, w, al, fn, sz, bold, col in vals:
        add_text(s, xx + 0.25, y + 0.18, w - 0.30, row_h,
                 [{"text": v, "font": fn, "size": sz, "bold": bold, "color": col}],
                 align=al)
        xx += w
    y += row_h

# Takeaway banner
add_rect(s, 0.70, 5.50, 12.00, 1.40, TEAL)
add_text(s, 0.95, 5.70, 11.50, 0.30,
         [{"text": "WHAT IT MEANS — AND THE CAVEAT", "font": FONT_SANS, "size": 10,
           "bold": True, "color": BEIGE}])
add_text(s, 0.95, 6.05, 11.50, 0.80,
         [{"text": "On labeled MIMIC-III data, TF-IDF + RF wins every metric. "
                   "But these sentences are clean and uniform. Real MIMIC-IV "
                   "discharge notes are a very different distribution — the next "
                   "three slides show what happens when we apply each model there.",
           "font": FONT_SERIF, "size": 14, "color": CREAM}])


# ========================================================================
# SLIDE 8 — MIMIC-IV SMI Cohort
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "INFERENCE DATA", 8)
add_title(s, "Scaling the baselines to real discharge notes")

# Left: description
add_eyebrow(s, 0.70, 2.30, "WHAT MIMIC-IV IS")
add_text(s, 0.70, 2.60, 7.80, 0.75,
         [{"text": "Successor to MIMIC-III: ~546K admissions at BIDMC "
                   "(2008–2019) with linked clinician-written discharge notes.",
           "font": FONT_SANS, "size": 13, "color": BLACK}])

add_eyebrow(s, 0.70, 3.55, "OUR COHORT")
add_text(s, 0.70, 3.85, 7.80, 0.75,
         [{"text": "3,808 admissions whose primary diagnosis is schizophrenia, "
                   "bipolar disorder, or severe/recurrent MDD (built in MS2).",
           "font": FONT_SANS, "size": 13, "color": BLACK}])

add_eyebrow(s, 0.70, 4.75, "WHY SMI SPECIFICALLY")
add_text(s, 0.70, 5.05, 7.80, 0.85,
         [{"text": "Clinical guidelines recommend housing be assessed and "
                   "documented at discharge for SMI patients. We want to "
                   "measure how often that actually happens.",
           "font": FONT_SANS, "size": 13, "color": BLACK}])

add_eyebrow(s, 0.70, 6.05, "PREPROCESSING")
add_text(s, 0.70, 6.35, 7.80, 0.60,
         [{"text": "Split each note into sentences; drop non-narrative "
                   "sections (labs, meds, physical exam, admin headers).",
           "font": FONT_SANS, "size": 13, "color": BLACK}])

# Right: stats
add_big_stat(s, 9.20, 2.30, 3.80, "3,808", "SMI ADMISSIONS",
             "primary SMI diagnosis, post-exclusions")
add_big_stat(s, 9.20, 3.80, 3.80, "253K", "NARRATIVE SENTENCES",
             "after section + sentence filtering", stat_color=RUST)
add_big_stat(s, 9.20, 5.30, 3.80, "Unlabeled", "INFERENCE ONLY",
             "mention rate, not precision / recall")


# ========================================================================
# SLIDE 9 — Keyword Search on SMI
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "INFERENCE  ·  BASELINE 1", 9)
add_title(s, "Half the notes mention housing — by keyword search")

# Left: figure placeholder
add_figure_placeholder(s, 0.70, 2.20, 8.20, 4.00,
                       "Housing-mention share on the SMI cohort by keyword search")

# Right: stat
add_big_stat(s, 9.20, 2.20, 3.80, "50.9%", "OF SMI NOTES FLAGGED",
             "1,940 of 3,808 admissions", stat_size=42)

add_eyebrow(s, 9.20, 4.00, "CONCERN")
add_text(s, 9.20, 4.30, 3.80, 2.00,
         [{"text": "This estimate may overcount due to lexical false positives "
                   "— e.g., `street` fires on \"street drugs\" or \"street clothes\", "
                   "not just \"living on the street.\"",
           "font": FONT_SANS, "size": 12, "color": BLACK}])

# Bottom banner
add_rect(s, 0.70, 6.35, 12.00, 0.60, TEAL)
add_text(s, 0.95, 6.48, 11.50, 0.40,
         [{"text": "A reasonable ceiling, but inflated by homonyms. "
                   "Predictable failure mode.",
           "font": FONT_SERIF, "size": 13, "color": CREAM}])


# ========================================================================
# SLIDE 10 — TF-IDF + RF on SMI
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "INFERENCE  ·  BASELINE 2", 10)
add_title(s, "The RF flags almost nothing — what went wrong?")

# Left: figure placeholder
add_figure_placeholder(s, 0.70, 2.20, 8.20, 4.00,
                       "Agreement crosstab — TF-IDF + RF vs keyword search on SMI")

# Right: stat
add_big_stat(s, 9.20, 2.20, 3.80, "1.16%", "OF SMI NOTES FLAGGED",
             "44 of 3,808 admissions", stat_size=42, stat_color=RUST)

add_eyebrow(s, 9.20, 4.00, "WHY IT UNDERPERFORMS")
add_bullets(s, 9.20, 4.30, 3.80, 2.50,
            ["TF-IDF word vectors aren't semantic — exact vocabulary only",
             "MIMIC-III train sentences are uniform; MIMIC-IV discharge notes vary wildly in length and style"],
            size=11)

# Bottom banner
add_rect(s, 0.70, 6.35, 12.00, 0.60, TEAL)
add_text(s, 0.95, 6.48, 11.50, 0.40,
         [{"text": "Large distribution shift: clean synthetic sentences → "
                   "messy real clinical prose. Bag-of-words doesn't survive it.",
           "font": FONT_SERIF, "size": 13, "color": CREAM}])


# ========================================================================
# SLIDE 11 — W2V + MLP on SMI
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "INFERENCE  ·  BASELINE 3", 11)
add_title(s, "The MLP flags almost everything — a different failure mode")

# Left: figure placeholder
add_figure_placeholder(s, 0.70, 2.20, 8.20, 4.00,
                       "Agreement crosstab — Word2Vec + MLP vs keyword search on SMI")

# Right: stat
add_big_stat(s, 9.20, 2.20, 3.80, "83.2%", "OF SMI NOTES FLAGGED",
             "at tuned threshold 0.855", stat_size=42, stat_color=RUST)

add_eyebrow(s, 9.20, 4.00, "WHY IT OVER-FLAGS")
add_bullets(s, 9.20, 4.30, 3.80, 2.50,
            ["Semantic embeddings generalize better than TF-IDF — the model doesn't need exact vocabulary",
             "But averaging word vectors loses word order; `the` and `housing` get equal weight",
             "MIMIC-III ↔ MIMIC-IV distribution gap is large; raising threshold to 0.855 helped, not enough"],
            size=11)

# Bottom banner
add_rect(s, 0.70, 6.35, 12.00, 0.60, TEAL)
add_text(s, 0.95, 6.48, 11.50, 0.40,
         [{"text": "Motivates ClinicalBERT: contextual embeddings pre-trained "
                   "on clinical text, preserving word order.",
           "font": FONT_SERIF, "size": 13, "color": CREAM}])


# ========================================================================
# SLIDE 12 — Main Takeaways
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "SYNTHESIS", 12)
add_title(s, "What MS3 taught us")

# Five numbered cards in two rows
cards = [
    ("01", "ML baselines don't generalize from MIMIC-III to MIMIC-IV",
     "Both did well on held-out MIMIC-III sentences but fell apart on real discharge notes."),
    ("02", "TF-IDF + RF under-flags (1.2%); W2V + MLP over-flags (83%)",
     "Opposite failure modes, same root cause — a large train / inference distribution shift."),
    ("03", "Class imbalance amplified the problem",
     "89% non-housing / 11% housing; oversampling + class weights helped on val, not on MIMIC-IV."),
    ("04", "Preprocessing mattered more than expected",
     "Dropping non-narrative sections (labs, meds, headers) was essential before inference."),
    ("05", "Keyword search is the most trustworthy baseline for now",
     "Lower ceiling but predictable failure mode. Confirms the MS2 plan: move to ClinicalBERT."),
]
# Layout: 3 cards top row, 2 cards bottom row
positions = [
    (0.70, 2.20, 4.00, 2.10),
    (4.85, 2.20, 4.00, 2.10),
    (9.00, 2.20, 3.70, 2.10),
    (1.80, 4.45, 4.50, 2.45),
    (7.10, 4.45, 4.50, 2.45),
]
for (pos, card) in zip(positions, cards):
    left, top, w, h = pos
    num, title, body = card
    # Card background
    add_rect(s, left, top, w, h, WHITE, line=BEIGE)
    # Number
    add_text(s, left + 0.20, top + 0.15, 1.5, 0.60,
             [{"text": num, "font": FONT_SERIF, "size": 28, "bold": True, "color": RUST}])
    # Title
    add_text(s, left + 0.20, top + 0.75, w - 0.40, 0.80,
             [{"text": title, "font": FONT_SERIF, "size": 14, "bold": True, "color": TEAL}])
    # Body
    add_text(s, left + 0.20, top + h - 0.95, w - 0.40, 0.85,
             [{"text": body, "font": FONT_SANS, "size": 11, "color": BLACK}])


# ========================================================================
# SLIDE 13 — Next Steps
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_chrome(s, "NEXT STEPS", 13)
add_title(s, "What happens between now and the final deliverable")

# Left: three numbered steps
steps = [
    ("01", "Fine-tune",
     "Bio_ClinicalBERT on MIMIC-III-SDOH + weakly-labeled MIMIC-IV sentences. "
     "Class-weighted loss, F1-tuned threshold."),
    ("02", "Expand",
     "The training set by manually reviewing keyword-caught MIMIC-IV sentences "
     "(weak supervision) to close the distribution gap."),
    ("03", "Re-analyze",
     "Subgroup analysis mirroring MS2 breakdowns (race, insurance, gender, diagnosis) "
     "with the best classifier's predictions."),
]
y = 2.30
for num, title, body in steps:
    add_text(s, 0.70, y, 0.70, 0.55,
             [{"text": num, "font": FONT_SERIF, "size": 22, "bold": True, "color": RUST}])
    add_text(s, 1.50, y, 7.00, 0.55,
             [{"text": title.upper(), "font": FONT_SANS, "size": 11,
               "bold": True, "color": RUST}])
    add_text(s, 1.50, y + 0.35, 7.00, 1.00,
             [{"text": body, "font": FONT_SANS, "size": 13, "color": BLACK}])
    y += 1.50

# Right: responsibilities & open questions
add_rect(s, 9.00, 2.30, 3.80, 0.02, BEIGE)
add_eyebrow(s, 9.00, 2.40, "RESPONSIBILITIES")
add_text(s, 9.00, 2.75, 3.80, 1.50,
         [{"text": "Matlin and Brianna will share responsibilities equally "
                   "across all three steps.",
           "font": FONT_SERIF, "size": 14, "color": TEAL}])

add_eyebrow(s, 9.00, 4.30, "OPEN QUESTIONS FOR THE TF")
add_bullets(s, 9.00, 4.65, 3.80, 2.10,
            ["Is weak-supervision augmentation with keyword-caught MIMIC-IV sentences acceptable?",
             "Is a long-input transformer (ClinicalBERT-long, Longformer) worth the compute cost?"],
            size=11)


# ========================================================================
# SLIDE 14 — Thank You
# ========================================================================
s = prs.slides.add_slide(blank_layout)
add_rect(s, 0.0, 0.0, 13.333, 7.5, TEAL)

add_text(s, 1.0, 2.50, 11.3, 1.30,
         [{"text": "THANK YOU", "font": FONT_SANS, "size": 14,
           "bold": True, "color": BEIGE}])
add_text(s, 1.0, 2.95, 11.3, 1.50,
         [{"text": "Questions?", "font": FONT_SERIF, "size": 72,
           "bold": True, "color": CREAM}])

add_rect(s, 1.0, 4.70, 0.80, 0.08, RUST)

add_text(s, 1.0, 5.00, 11.3, 0.50,
         [{"text": "Matlin Gilman   ·   Brianna Grissom",
           "font": FONT_SERIF, "size": 20, "color": CREAM}])
add_text(s, 1.0, 5.55, 11.3, 0.40,
         [{"text": "Project #63   ·   AC209B   ·   Milestone 3",
           "font": FONT_SANS, "size": 11, "bold": True, "color": BEIGE}])


# ========================================================================
out = "/Users/briannagrissom/spring-2026-courses/AC209b/ehr-analysis/milestone3_presentation.pptx"
prs.save(out)
print(f"Saved: {out}")
print(f"Slides: {len(prs.slides)}")
