import streamlit as st
import random
import json
import streamlit.components.v1 as components

import toml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / ".streamlit" / "config.toml"


st.markdown("""
<style>
.question-prompt {
  font-family: inherit !important;
  font-size: 1.1em !important;
  font-weight: normal;
  color: #FFFFFF;
  text-align: center;
  margin-bottom: 1.5em;
  word-break: break-word;
  white-space: normal !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
.ayah-meta {
  font-family: inherit !important;
  font-size: 1.3em !important;
  font-weight: bold !important;
  color: #FFFFFF !important;
  text-align: center !important;
  margin-bottom: 0.45em !important;
  margin-top: 0.25em !important;
  width: 100%;
  display: block;
}
</style>
""", unsafe_allow_html=True)





# 1) your preset themes
THEMES = {
    "Teal": {
        "base": "dark",
        "primaryColor":             "#00FFFF",
        "backgroundColor":          "#051716",
        "secondaryBackgroundColor": "#062422",
        "textColor":                "#FFFFFF",
    },
    "Blue": {
        "base": "dark",
        "primaryColor":             "#0059FF",
        "backgroundColor":          "#050917",
        "secondaryBackgroundColor": "#060C24",
        "textColor":                "#FFFFFF",
    },
    "Purple": {
        "base": "dark",
        "primaryColor":             "#8A00FF",
        "backgroundColor":          "#0D0517",
        "secondaryBackgroundColor": "#120624",
        "textColor":                "#FFFFFF",
    },
    "Magenta": {
        "base": "dark",
        "primaryColor":             "#FF00FF",
        "backgroundColor":          "#160517",
        "secondaryBackgroundColor": "#220624",
        "textColor":                "#FFFFFF",
    },
    "Red": {
        "base": "dark",
        "primaryColor":             "#FF0030",
        "backgroundColor":          "#170506",
        "secondaryBackgroundColor": "#240607",
        "textColor":                "#FFFFFF",
    },
    "Orange": {
        "base": "dark",
        "primaryColor":             "#FF6600",  # more saturated orange
        "backgroundColor":          "#1A0E03",
        "secondaryBackgroundColor": "#261503",
        "textColor":                "#FFFFFF",
    },
    "Green": {
        "base": "dark",
        "primaryColor":             "#00FF66",  # rich neon green
        "backgroundColor":          "#05170B",
        "secondaryBackgroundColor": "#062415",
        "textColor":                "#FFFFFF",
    },
    "Gold": {
        "base": "dark",
        "primaryColor":             "#FFD700",  # true gold
        "backgroundColor":          "#171403",
        "secondaryBackgroundColor": "#241E06",
        "textColor":                "#FFFFFF",  # better contrast on gold
    },
}

cfg = toml.load(CONFIG_PATH)
current_colors = cfg.get("theme", {})

def get_theme_name_by_colors(theme_dict):
    for name, theme in theme_dict.items():
        if all(theme.get(k) == current_colors.get(k) for k in ["primaryColor", "backgroundColor", "secondaryBackgroundColor", "textColor"]):
            return name
    return list(theme_dict.keys())[0]  # fallback to the first theme if none match

current_theme_name = get_theme_name_by_colors(THEMES)

def write_theme_to_config(theme_dict):
    # load existing file (to preserve other settings)
    cfg = toml.load(CONFIG_PATH)
    cfg["theme"] = theme_dict
    with open(CONFIG_PATH, "w") as f:
        toml.dump(cfg, f)

# — Custom Arabic‐only font styling —
st.markdown("""
<style>
  /* 1) load your preferred Arabic face */
  @font-face {
  font-family: 'Nafees Nastaleeq';
  src: url('/assets/fonts/NafeesNastaleeq.woff2') format('woff2'),
       url('/assets/fonts/NafeesNastaleeq.woff') format('woff');
  font-weight: bold;
  font-style: bold;
}


div[dir="rtl"] {
  font-family: 'Nafees Nastaleeq', serif !important;
  font-size: 1.4em !important;
  line-height: 1.8 !important;
  letter-spacing: 0.07em !important;   /* tweak this value to taste */

}
</style>
""", unsafe_allow_html=True)

# - Hide expander icons -
st.markdown("""
<style>
  [data-testid="stExpander"] > div:first-child svg,
  div[data-testid="stExpanderHeader"] svg { display: none!important; }
</style>
""", unsafe_allow_html=True)

# - Load Quran data -
with open("master_quran.json", "r", encoding="utf-8") as f:
    quran_data = json.load(f)

# - Metadata for filters -
surah_names = {a["surah"]: a["surah_name"] for a in quran_data}
all_surah   = sorted({a["surah"] for a in quran_data})
all_juzz    = sorted({a["juzz"]  for a in quran_data})
all_quarter = sorted({a["quarter"] for a in quran_data})

# - Title centered -
st.markdown('<h1 style="text-align: center;">Quran Mastery Trainer</h1>', unsafe_allow_html=True)

# - Filtering helpers -
def in_ruku(a):
    return any(a["juzz"]==j and s<=a["ruku"]<=e for j,s,e in st.session_state.get("active_ruku", []))

def in_ayah(a):
    return any(a["surah"]==s and s2<=a["ayah"]<=e2 for s,s2,e2 in st.session_state.get("active_ayah", []))

# - Sidebar controls -


st.sidebar.markdown("### Pick a theme")
choice = st.sidebar.selectbox(
    "Theme preset", 
    list(THEMES.keys()), 
    index=list(THEMES.keys()).index(current_theme_name)
)

# ← Replace your old Apply‐Theme block with this:
if st.sidebar.button("Apply Theme"):
    write_theme_to_config(THEMES[choice])
    st.sidebar.success(f"Theme “{choice}” written. Refreshing…")

    # inject JS that reloads the top‐level window, not just the iframe
    components.html(
        """
        <script>
          setTimeout(function() {
            // reload the parent page (the Streamlit app itself)
            window.parent.location.reload();
          }, 1000);
        </script>
        """,
        height=0,
        width=0,
    )
    st.stop()



with st.sidebar:
    with st.expander("Manage Standard Filters", expanded=False):
        juzz_sel    = st.multiselect("Juzz",    all_juzz)
        quarter_sel = st.multiselect("Quarter", all_quarter)
        surah_sel   = st.multiselect(
            "Surah", all_surah,
            format_func=lambda x: f"{x} – {surah_names[x]}"
        )

    # Ruku range filters
    with st.expander("Manage Ruku Ranges", expanded=False):
        if "ruku_ranges" not in st.session_state:
            st.session_state.ruku_ranges = []
        r_start = st.number_input("Ruku start", min_value=1, step=1, key="rstart2")
        r_end   = st.number_input("Ruku end",   min_value=1, step=1, key="rend2")
        r_juzz  = st.selectbox("Juzz for this Ruku range", all_juzz, key="rjuzz2")
        if st.button("Add Ruku Range", key="add_ruku"):
            max_r = max(a["ruku"] for a in quran_data if a["juzz"] == r_juzz)
            new_range = (r_juzz, r_start, r_end)
            if r_start > r_end:
                st.error("Start must be ≤ end.")
            elif r_end > max_r:
                st.error(f"Juzz {r_juzz} has only {max_r} rukus.")
            elif new_range in st.session_state.ruku_ranges:
                st.warning("That Ruku range is already added.")
            else:
                st.session_state.ruku_ranges.append(new_range)
        labels = [f"J{j}-R{a}-{b}" for j,a,b in st.session_state.ruku_ranges]
        active = st.multiselect("Active Ruku Ranges", labels, default=labels)
        # Only keep ranges that are still selected
        st.session_state.ruku_ranges = [rng for rng, lab in zip(st.session_state.ruku_ranges, labels) if lab in active]
        st.session_state.active_ruku = st.session_state.ruku_ranges

    # Ayah range filters
    with st.expander("Manage Ayah Ranges", expanded=False):
        if "ayah_ranges" not in st.session_state:
            st.session_state.ayah_ranges = []
        a_start = st.number_input("Ayah start", min_value=1, step=1, key="astart2")
        a_end   = st.number_input("Ayah end",   min_value=1, step=1, key="aend2")
        a_surah = st.selectbox("Surah for this Ayah range", all_surah, key="asurah2")
        if st.button("Add Ayah Range", key="add_ayah"):
            new_range = (a_surah, a_start, a_end)
            if a_start > a_end:
                st.error("Start must be ≤ end.")
            elif new_range in st.session_state.ayah_ranges:
                st.warning("That Ayah range is already added.")
            else:
                st.session_state.ayah_ranges.append(new_range)
        labels = [f"S{s}:{a}-{b}" for s,a,b in st.session_state.ayah_ranges]
        active = st.multiselect("Active Ayah Ranges", labels, default=labels)
        # Only keep ranges that are still selected
        st.session_state.ayah_ranges = [rng for rng, lab in zip(st.session_state.ayah_ranges, labels) if lab in active]
        st.session_state.active_ayah = st.session_state.ayah_ranges


    # Compute filtered list
    filtered = [
        a for a in quran_data
        if ((juzz_sel    and a["juzz"]    in juzz_sel)
         or (quarter_sel and a["quarter"] in quarter_sel)
         or (surah_sel   and a["surah"]   in surah_sel)
         or in_ruku(a)
         or in_ayah(a))
    ]
    filtered_sorted = sorted(filtered, key=lambda x: (x["surah"], x["ayah"]))

    st.markdown(f"**Total matching ayahs: {len(filtered_sorted)}**")
    st.markdown("---")
    gen = st.button("Generate Challenge Questions")
    mode = st.radio("Mode", options=["Study Mode", "Test Mode"], index=0, key="mode")
    include_info = st.checkbox("Include Ayah Info", value=False)



# - Initialize session state -
if "questions" not in st.session_state:
    st.session_state.questions = []
if "revealed" not in st.session_state:
    st.session_state.revealed = {}

# - Friendly labels for drill types -
LABELS = {
    "random_keys": "Random Ayahs",
    "random_keys_following": "Random Ayahs (Following)",
    "random_keys_previous": "Random Ayahs (Previous)",
    "range_drill": "Limited Range Recital",
    "reverse_range_drill": "Reverse Limited Range Recital",
    "ruku_drill": "Ruku Recital",
    "ruku_last_drill": "Ruku Last Recital",
    "next_ruku_first_drill": "Next Ruku Recital",
    "next_ruku_last_drill": "Next Ruku First Ayah Drill",
    "skip_ayah_drill": "Ayah Intervals"
}

# - Fixed sequence of question types -
QUESTION_TYPE_ORDER = [
    "random_keys",
    "random_keys_following",
    "random_keys_previous",
    "range_drill",
    "reverse_range_drill",
    "ruku_drill",
    "ruku_last_drill",
    "next_ruku_first_drill",
    "next_ruku_last_drill",
  "skip_ayah_drill"

]

# - Generate questions on click -
if gen:
    if not filtered_sorted:
        st.error("❗ Please select a range (Juzz, Surah, Quarter, Ruku, or Ayah range) **before** generating questions!")
        st.stop()  # Prevents any further code from running (including accidental clearing of questions!)
    qs = []
    total = len(filtered_sorted)

# - Generate questions on click -
if gen:
    qs = []
    total = len(filtered_sorted)

    # Q1: Random Ayahs
    if "random_keys" in QUESTION_TYPE_ORDER:
        if mode == "Study Mode":
            picks = filtered_sorted.copy()
            random.shuffle(picks)
        else:
            count = min(int(0.6 * total), 20)
            picks = random.sample(filtered_sorted, count)
            random.shuffle(picks)
        keys = [p["ayah_key"] for p in picks]
        qs.append({
            "type": "random_keys",
            "content": f"Recite the following ayahs: {', '.join(keys)}",
            "answers": picks
        })

    # Q2: Random Ayahs (Following)
    if "random_keys_following" in QUESTION_TYPE_ORDER:
        if mode == "Study Mode":
            working = filtered_sorted.copy()
            random.shuffle(working)
        else:
            count = min(int(0.6 * total), 20)
            working = random.sample(filtered_sorted, count)
            random.shuffle(working)
        # exclude last ayah since no following
        picks = [a for a in working
                 if next((i for i, x in enumerate(filtered_sorted)
                          if x["ayah_key"] == a["ayah_key"]), total-1) < total-1]
        keys = [p["ayah_key"] for p in picks]
        answers = []
        for p in picks:
            idx = next(i for i, a in enumerate(filtered_sorted)
                       if a["ayah_key"] == p["ayah_key"])
            answers.append(filtered_sorted[idx+1])
        qs.append({
            "type": "random_keys_following",
            "content": f"Recite the ayah following these ayahs: {', '.join(keys)}",
            "answers": answers
        })

    # Q3: Random Ayahs (Previous)
    if "random_keys_previous" in QUESTION_TYPE_ORDER:
        if mode == "Study Mode":
            working = filtered_sorted.copy()
            random.shuffle(working)
        else:
            count = min(int(0.6 * total), 20)
            working = random.sample(filtered_sorted, count)
            random.shuffle(working)
        # exclude first ayah since no previous
        picks = [a for a in working
                 if next((i for i, x in enumerate(filtered_sorted)
                          if x["ayah_key"] == a["ayah_key"]), 0) > 0]
        keys = [p["ayah_key"] for p in picks]
        answers = []
        for p in picks:
            idx = next(i for i, a in enumerate(filtered_sorted)
                       if a["ayah_key"] == p["ayah_key"])
            answers.append(filtered_sorted[idx-1])
        qs.append({
            "type": "random_keys_previous",
            "content": f"Recite the ayah preceding these ayahs: {', '.join(keys)}",
            "answers": answers
        })

    # Q4: Limited Range Recital
    if "range_drill" in QUESTION_TYPE_ORDER:
        if mode == "Study Mode":
            # 1. Pick a single random ayah
            pick = random.choice(filtered_sorted)
            start_key = pick["ayah_key"]
            j, r = pick["juzz"], pick["ruku"]

            # 2. Look for all verses in the next ruku within the filtered range
            next_ruku = r + 1
            next_ruku_verses = [
                a for a in filtered_sorted
                if a["juzz"] == j and a["ruku"] == next_ruku
            ]

            if next_ruku_verses:
                # 3a. If the next ruku exists, end at its last ayah
                end_key = next_ruku_verses[-1]["ayah_key"]
                start_idx = next(i for i, a in enumerate(filtered_sorted)
                                 if a["ayah_key"] == start_key)
                end_idx = next(i for i, a in enumerate(filtered_sorted)
                               if a["ayah_key"] == end_key)
                answers = filtered_sorted[start_idx:end_idx+1]
                content = (
                    f"Recite from ayah {start_key} until the end of the next ruku "
                    f"– ayah {end_key}."
                )
            else:
                # 3b. Otherwise end at the very end of the selected range
                end_key = filtered_sorted[-1]["ayah_key"]
                start_idx = next(i for i, a in enumerate(filtered_sorted)
                                 if a["ayah_key"] == start_key)
                answers = filtered_sorted[start_idx:]
                content = (
                    f"Recite from ayah {start_key} till the end of the selected range "
                    f"– ayah {end_key}."
                )

            qs.append({
                "type": "range_drill",
                "content": content,
                "answers": answers
            })
        else:
            # Test Mode logic: Limited Range Recital to next quarter (with wrap)
            pick = random.choice(filtered_sorted)
            start_key = pick["ayah_key"]
            j = pick["juzz"]
            current_quarter = int(pick.get("quarter"))
            # Determine next quarter and adjust juzz if wrapping
            if current_quarter < 4:
                next_quarter = current_quarter + 1
                next_juzz = j
            else:
                next_quarter = 1
                next_juzz = j + 1

            # Find verses in the next quarter using full Quran data
            next_quarter_verses = [
                a for a in quran_data
                if a["juzz"] == next_juzz and int(a.get("quarter", 0)) == next_quarter
            ]

            if next_quarter_verses:
                end_key = next_quarter_verses[-1]["ayah_key"]
                start_idx = next(i for i, a in enumerate(quran_data)
                                 if a["ayah_key"] == start_key)
                end_idx = next(i for i, a in enumerate(quran_data)
                               if a["ayah_key"] == end_key)
                answers = quran_data[start_idx:end_idx+1]
                content = (
                    f"Recite from ayah {start_key} to the end of the next quarter "
                    f"– ayah {end_key}."
                )
            else:
                # Fallback to end of selected range
                end_key = filtered_sorted[-1]["ayah_key"]
                start_idx = next(i for i, a in enumerate(filtered_sorted)
                                 if a["ayah_key"] == start_key)
                answers = filtered_sorted[start_idx:]
                content = (
                    f"Recite from ayah {start_key} till the end of the selected range "
                    f"– ayah {end_key}."
                )

            qs.append({
                "type": "range_drill",
                "content": content,
                "answers": answers
            })

    # Q5: Reverse Limited Range Recital
    if "reverse_range_drill" in QUESTION_TYPE_ORDER:
        if mode == "Study Mode":
            pick = random.choice(filtered_sorted)
            start_key = pick["ayah_key"]
            j, r = pick["juzz"], pick["ruku"]
            prev_ruku = r - 1
            if prev_ruku >= 1:
                prev_ruku_verses = [
                    a for a in filtered_sorted if a["juzz"] == j and a["ruku"] == prev_ruku
                ]
                end_key = prev_ruku_verses[0]["ayah_key"]
                start_idx = next(i for i, a in enumerate(filtered_sorted)
                                 if a["ayah_key"] == start_key)
                end_idx = next(i for i, a in enumerate(filtered_sorted)
                               if a["ayah_key"] == end_key)
                answers = filtered_sorted[end_idx:start_idx+1]
                content = (f"Recite backwards from ayah {start_key} to the start of the previous ruku "
                           f"– ayah {end_key}.")
            else:
                end_key = filtered_sorted[0]["ayah_key"]
                start_idx = next(i for i, a in enumerate(filtered_sorted)
                                 if a["ayah_key"] == start_key)
                answers = filtered_sorted[0:start_idx+1]
                content = (f"Recite backwards from ayah {start_key} till the start of the selected range "
                           f"– ayah {end_key}.")
            answers = list(reversed(answers))
            qs.append({"type": "reverse_range_drill", "content": content, "answers": answers})
        else:
            pick = random.choice(filtered_sorted)
            start_key = pick["ayah_key"]
            j = pick["juzz"]
            current_quarter = int(pick.get("quarter"))
            if current_quarter > 1:
                prev_quarter = current_quarter - 1
                prev_juzz = j
            else:
                prev_quarter = 4
                prev_juzz = j - 1
            prev_quarter_verses = [
                a for a in quran_data if a["juzz"] == prev_juzz and int(a.get("quarter", 0)) == prev_quarter
            ]
            if prev_quarter_verses:
                end_key = prev_quarter_verses[0]["ayah_key"]
                start_idx = next(i for i, a in enumerate(quran_data)
                                 if a["ayah_key"] == start_key)
                end_idx = next(i for i, a in enumerate(quran_data)
                               if a["ayah_key"] == end_key)
                answers = quran_data[end_idx:start_idx+1]
                content = (f"Recite backwards from ayah {start_key} to the start of the previous quarter "
                           f"– ayah {end_key}.")
            else:
                end_key = filtered_sorted[0]["ayah_key"]
                start_idx = next(i for i, a in enumerate(filtered_sorted)
                                 if a["ayah_key"] == start_key)
                answers = filtered_sorted[0:start_idx+1]
                content = (f"Recite backwards from ayah {start_key} till the start of the selected range "
                           f"– ayah {end_key}.")
            answers = list(reversed(answers))
            qs.append({"type": "reverse_range_drill", "content": content, "answers": answers})

    # Q6: Ruku Drill
    if "ruku_drill" in QUESTION_TYPE_ORDER:
        # Collect unique (juzz, ruku) pairs in the filtered selection
        all_pairs = [(v["juzz"], v["ruku"]) for v in filtered_sorted]
        seen = set()
        pairs = []
        for pair in all_pairs:
            if pair not in seen:
                seen.add(pair)
                pairs.append(pair)

        if mode == "Study Mode":
            # Every ruku in a random order
            random.shuffle(pairs)
            picks = pairs
        else:
            # Test Mode: if <=8 rukus, shuffle all; otherwise pick 8-10 randomly
            total_pairs = len(pairs)
            if total_pairs <= 8:
                picks = pairs.copy()
                random.shuffle(picks)
            else:
                count = random.randint(8, 10)
                picks = random.sample(pairs, count)

        # Content: list Juzz & Ruku pairs
        keys = [f"J{j}-R{r}" for j, r in picks]
        content = f"Recite the first 5 ayahs of the following rukus: {', '.join(keys)}"

        # Answers: first 5 ayahs of each
        answers = []
        for j, r in picks:
            ayahs = [a for a in filtered_sorted if a["juzz"] == j and a["ruku"] == r]
            answers.extend(ayahs[:5])

        qs.append({
            "type": "ruku_drill",
            "content": content,
            "answers": answers
        })

# Q7: Ruku Last Ayahs Drill
    if "ruku_last_drill" in QUESTION_TYPE_ORDER:
        # Collect unique (juzz, ruku) pairs in the filtered selection
        all_pairs = [(v["juzz"], v["ruku"]) for v in filtered_sorted]
        seen = set()
        pairs = []
        for pair in all_pairs:
            if pair not in seen:
                seen.add(pair)
                pairs.append(pair)

        if mode == "Study Mode":
            random.shuffle(pairs)
            picks = pairs
        else:
            total_pairs = len(pairs)
            if total_pairs <= 8:
                picks = pairs.copy()
                random.shuffle(picks)
            else:
                count = random.randint(8, 10)
                picks = random.sample(pairs, count)

        # Content: list Juzz & Ruku pairs
        keys = [f"J{j}-R{r}" for j, r in picks]
        content = f"Recite the last 5 ayahs of the following rukus: {', '.join(keys)}"

        # Answers: last 5 ayahs of each
        answers = []
        for j, r in picks:
            ayahs = [a for a in filtered_sorted if a["juzz"] == j and a["ruku"] == r]
            answers.extend(ayahs[-5:])

        qs.append({
            "type": "ruku_last_drill",
            "content": content,
            "answers": answers
        })

    # Q8: Next Ruku First Ayah Drill (fixed to avoid empty picks)
    if "next_ruku_first_drill" in QUESTION_TYPE_ORDER:
        # 1) Build de‐duplicated list of (juzz, ruku)
        all_pairs = [(v["juzz"], v["ruku"]) for v in filtered_sorted]
        seen = set(); pairs = []
        for p in all_pairs:
            if p not in seen:
                seen.add(p)
                pairs.append(p)

        # 2) If there's no “next” ruku at all, skip this question
        if len(pairs) < 2:
            # nothing to quiz on
            pass
        else:
            # 3) Only pick among those with at least one successor
            valid_starts = pairs[:-1]
            start_j, start_r = random.choice(valid_starts)
            idx = pairs.index((start_j, start_r))

            # 4) Determine how many next rukus to include
            if mode == "Study Mode":
                picks = pairs[idx+1:]
            else:
                remaining = len(pairs) - (idx + 1)
                if remaining < 3:
                    picks = pairs[idx+1:]
                else:
                    x = random.randint(3, min(10, remaining))
                    picks = pairs[idx+1 : idx+1 + x]

            # 5) Build prompt (only shows the very next one)
            count = len(picks)
            first_j, first_r = picks[0]
            content = (
                f"Recite the first ayah of the next {count} rukus starting from "
                f"J{first_j} Ruku {first_r}"
            )

            # 6) Gather answers for all picks
            answers = []
            for j, r in picks:
                ay = next((a for a in filtered_sorted 
                           if a["juzz"]==j and a["ruku"]==r), None)
                if ay:
                    answers.append(ay)

            qs.append({
                "type":    "next_ruku_first_drill",
                "content": content,
                "answers": answers
            })

    # Q9: Last Ruku Last Ayah Drill
    if "next_ruku_last_drill" in QUESTION_TYPE_ORDER:
        # 1) Build a de‐duplicated list of (juzz, ruku) pairs
        all_pairs = [(v["juzz"], v["ruku"]) for v in filtered_sorted]
        seen = set()
        pairs = []
        for p in all_pairs:
            if p not in seen:
                seen.add(p)
                pairs.append(p)

        # 2) If there's fewer than 2 rukus, skip (no “next” to ask)
        if len(pairs) < 2:
            pass
        else:
            # 3) Only pick starting points that have at least one successor
            valid_starts = pairs[:-1]
            start_j, start_r = random.choice(valid_starts)
            idx = pairs.index((start_j, start_r))

            # 4) Select which “next” rukus to quiz on
            if mode == "Study Mode":
                picks = pairs[idx+1:]
            else:
                remaining = len(pairs) - (idx + 1)
                if remaining < 3:
                    picks = pairs[idx+1:]
                else:
                    x = random.randint(3, min(10, remaining))
                    picks = pairs[idx+1 : idx+1 + x]

            # 5) Build the prompt (showing only the very next ruku)
            count = len(picks)
            first_j, first_r = picks[0]
            content = (
                f"Recite the last ayah of the next {count} rukus: "
                f"J{first_j} Ruku {first_r}"
            )

            # 6) Gather the correct answers (last ayah of each picked ruku)
            answers = []
            for j, r in picks:
                ayahs = [a for a in filtered_sorted if a["juzz"] == j and a["ruku"] == r]
                if ayahs:
                    answers.append(ayahs[-1])

            qs.append({
                "type":    "next_ruku_last_drill",
                "content": content,
                "answers": answers
            })

    # Q10: Every Nth Ayah Drill
    if "skip_ayah_drill" in QUESTION_TYPE_ORDER:
        ayahs = filtered_sorted  # list of all ayah dicts in order

        # only proceed if there's at least one “next” ayah
        if len(ayahs) > 1:
            # 1) pick a start ayah (never the very last one)
            start = random.choice(ayahs[:-1])
            idx   = ayahs.index(start)

            # 2) pick a step x between 2 and 5
            step = random.randint(2, 5)

            # 3) decide how many to collect
            max_count = 5 if mode == "Study Mode" else 10

            # 4) gather every step-th ayah
            picks = []
            pos   = idx
            while pos < len(ayahs) and len(picks) < max_count:
                picks.append(ayahs[pos])
                pos += step

            # how many we actually got
            count = len(picks)

            # build the ordinal suffix
            suffix_map = {1: "st", 2: "nd", 3: "rd"}
            suffix     = suffix_map.get(step, "th")
            ordinal    = f"{step}{suffix}"

            # starting point
            s, a = start["surah"], start["ayah"]

            # ending point
            last_s, last_a = picks[-1]["surah"], picks[-1]["ayah"]

            # 5) build the prompt: mention either the count or that it runs to the end of range
            if count < max_count:
                content = (
                    f"Recite every {ordinal} ayah from {s}:{a} "
                    f"until the end of the selected range (ending at {last_s}:{last_a})"
                )
            else:
                content = (
                    f"Recite every {ordinal} ayah from {s}:{a} for {count} ayahs"
                )

            # 6) append to your questions
            qs.append({
                "type":    "skip_ayah_drill",
                "content": content,
                "answers": picks
            })

    # Save and reset reveal counters
    st.session_state.questions = qs
    st.session_state.revealed = {f"q{i}": 0 for i in range(len(qs))}


# - Render questions & answers -

def render_question(i, q):
    key = f"q{i}"
    if key not in st.session_state.revealed:
        st.session_state.revealed[key] = 0

    qtype = LABELS[q["type"]]
    with st.expander(f"Question {i+1} – {qtype}", expanded=True):
        # Question prompt styled
        st.markdown(
            f'<div class="question-prompt">{q["content"]}</div>',
            unsafe_allow_html=True
        )

        # four cols: big, button, button, big
        col0, col1, col2, col3 = st.columns([1.7,1,1,1.5])
        if col1.button("Reveal Next", key=f"btn_next_{i}"):
            cur = st.session_state.revealed[key]
            st.session_state.revealed[key] = min(cur + 1, len(q["answers"]))
        if col2.button("Reveal All", key=f"btn_all_{i}"):
            st.session_state.revealed[key] = len(q["answers"])

        to_show = st.session_state.revealed[key]
        if to_show > 0:
            st.markdown("---")
            for a in q["answers"][:to_show]:
                if include_info:
                    meta = f"Juzz {a['juzz']}, Ruku {a['ruku']}, Ayah {a['ayah_key']} <br>"
                    html  = f"<div class='ayah-meta'>{meta}</div>"
                    html += "<div dir='rtl' style='text-align: center; margin-bottom:1em;'>"
                    html += a['text']
                    html += "</div>"
                else:
                    html  = "<div dir='rtl' style='text-align: center; margin-bottom:1em;'>"
                    html += f"{a['text']} - ({a['ayah_key']})"
                    html += "</div>"
                st.markdown(html, unsafe_allow_html=True)




# - Display if questions exist -
if st.session_state.questions:
    st.markdown('<h2 style="text-align: center;">Your Challenge Questions</h2>', unsafe_allow_html=True)
    for idx, q in enumerate(st.session_state.questions):
        render_question(idx, q)
