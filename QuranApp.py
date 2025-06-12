import streamlit as st
import random
import json

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
  letter-spacing: 0.05em !important;   /* tweak this value to taste */

}


</style>
""", unsafe_allow_html=True)

# — your existing CSS to hide expanders etc. —
st.markdown("""
<style>
  /* hide expander icons */
  [data-testid="stExpander"] > div:first-child svg,
  div[data-testid="stExpanderHeader"] svg { display: none!important; }
  /* ...the rest of your CSS... */
</style>
""", unsafe_allow_html=True)

# — Load Quran data —
with open("master_quran.json", "r", encoding="utf-8") as f:
    quran_data = json.load(f)

# — Metadata for filters —
surah_names = {a["surah"]: a["surah_name"] for a in quran_data}
all_surah   = sorted({a["surah"] for a in quran_data})
all_juzz    = sorted({a["juzz"]  for a in quran_data})
all_quarter = sorted({a["quarter"] for a in quran_data})

# — Title centered —
st.markdown('<h1 style="text-align: center;">Quran Mastery Trainer</h1>', unsafe_allow_html=True)

# — Sidebar: filters and controls —
# Filtering helpers
def in_ruku(a):
    return any(a["juzz"]==j and s<=a["ruku"]<=e for j,s,e in st.session_state.get("active_ruku", []))

def in_ayah(a):
    return any(a["surah"]==s and s2<=a["ayah"]<=e2 for s,s2,e2 in st.session_state.get("active_ayah", []))

# Sidebar layout
with st.sidebar:
    with st.expander("Manage Standard Filters", expanded=False):
        juzz_sel    = st.multiselect("Juzz",    all_juzz)
        quarter_sel = st.multiselect("Quarter", all_quarter)
        surah_sel   = st.multiselect(
            "Surah", all_surah,
            format_func=lambda x: f"{x} – {surah_names[x]}"
        )

    filtered = [
        a for a in quran_data
        if ((juzz_sel    and a["juzz"]    in juzz_sel)
         or (quarter_sel and a["quarter"] in quarter_sel)
         or (surah_sel   and a["surah"]   in surah_sel)
         or in_ruku(a)
         or in_ayah(a))
    ]
    filtered_sorted = sorted(filtered, key=lambda x: (x["surah"], x["ayah"]))

    with st.expander("Manage Ruku Ranges", expanded=False):
        if "ruku_ranges" not in st.session_state:
            st.session_state.ruku_ranges = []
        r_start = st.number_input("Ruku start", min_value=1, step=1, key="rstart2")
        r_end   = st.number_input("Ruku end",   min_value=1, step=1, key="rend2")
        r_juzz  = st.selectbox("Juzz for this Ruku range", all_juzz, key="rjuzz2")
        if st.button("Add Ruku Range", key="add_ruku"):
            max_r = max(a["ruku"] for a in quran_data if a["juzz"] == r_juzz)
            if r_start > r_end:
                st.error("Start must be ≤ end.")
            elif r_end > max_r:
                st.error(f"Juzz {r_juzz} has only {max_r} rukus.")
            else:
                st.session_state.ruku_ranges.append((r_juzz, r_start, r_end))
        labels = [f"J{j}-R{a}-{b}" for j,a,b in st.session_state.ruku_ranges]
        active = st.multiselect("Active Ruku Ranges", labels, default=labels)
        st.session_state.active_ruku = [rng for rng,lab in zip(st.session_state.ruku_ranges, labels) if lab in active]

    with st.expander("Manage Ayah Ranges", expanded=False):
        if "ayah_ranges" not in st.session_state:
            st.session_state.ayah_ranges = []
        a_start = st.number_input("Ayah start", min_value=1, step=1, key="astart2")
        a_end   = st.number_input("Ayah end",   min_value=1, step=1, key="aend2")
        a_surah = st.selectbox("Surah for this Ayah range", all_surah, key="asurah2")
        if st.button("Add Ayah Range", key="add_ayah"):
            if a_start > a_end:
                st.error("Start must be ≤ end.")
            else:
                st.session_state.ayah_ranges.append((a_surah, a_start, a_end))
        labels = [f"S{s}:{a}-{b}" for s,a,b in st.session_state.ayah_ranges]
        active = st.multiselect("Active Ayah Ranges", labels, default=labels)
        st.session_state.active_ayah = [rng for rng,lab in zip(st.session_state.ayah_ranges, labels) if lab in active]

    st.markdown(f"**Total matching ayahs: {len(filtered_sorted)}**")

    st.markdown("---")
    gen = st.button("Generate Challenge Questions")
    st.markdown('<div style="text-align: center; margin-bottom: 0rem;">', unsafe_allow_html=True)
    include_info = st.checkbox("Include Ayah Info in answers", value=False)
    st.markdown('</div>', unsafe_allow_html=True)

# — Initialize session state —
if "questions" not in st.session_state:
    st.session_state.questions = []
if "revealed" not in st.session_state:
    st.session_state.revealed = {}

# — Drill size constants —
SEQ_MIN, SEQ_MAX   = 15, 25
RUKU_MIN, RUKU_MAX = 6,  12
KEYS_MIN, KEYS_MAX = 10, 15

# — Friendly labels for drill types —
LABELS = {
    "sequence":    "Sequence Recall",
    "ruku_first":  "First Ayahs of Ruku",
    "ruku_last":   "Last Ayahs of Ruku",
    "random_keys": "Random Keys Drill",
}

# — Generate questions on click —
if gen:
    if len(filtered_sorted) < SEQ_MIN:
        st.warning(f"Select at least {SEQ_MIN} ayahs to generate.")
    else:
        qs = []
        for _ in range(5):
            drill = random.choice(["sequence", "ruku_first", "ruku_last", "random_keys"])
            if drill == "sequence":
                ay = random.choice(filtered_sorted)
                idx0 = next(i for i,a in enumerate(filtered_sorted) if a["ayah_key"] == ay["ayah_key"])
                dirc = random.choice(["forward","backward"])
                req  = random.randint(SEQ_MIN, SEQ_MAX)
                seq  = (filtered_sorted[idx0: idx0+req] if dirc=="forward"
                        else filtered_sorted[max(0, idx0-req+1): idx0+1][::-1])
                content, answers = (f"Recite {len(seq)} ayahs {dirc} starting from {ay['ayah_key']}", seq)
            elif drill == "ruku_first":
                ru_list = sorted({a["ruku"] for a in filtered_sorted})
                start, dirc = random.choice(ru_list), random.choice(["forward","backward"])
                req, si    = random.randint(RUKU_MIN, RUKU_MAX), ru_list.index(start)
                target     = (ru_list[si: si+req] if dirc=="forward"
                              else ru_list[max(0, si-req+1): si+1][::-1])
                content    = f"Recite first ayahs of {len(target)} rukus {dirc} from Juzz {start}"
                answers    = [min((a for a in filtered_sorted if a["ruku"]==r), key=lambda x:(x["surah"],x["ayah"])) for r in target]
            elif drill == "ruku_last":
                ru_list = sorted({a["ruku"] for a in filtered_sorted})
                start, dirc = random.choice(ru_list), random.choice(["forward","backward"])
                req, si    = random.randint(RUKU_MIN, RUKU_MAX), ru_list.index(start)
                target     = (ru_list[si: si+req] if dirc=="forward"
                              else ru_list[max(0, si-req+1): si+1][::-1])
                content    = f"Recite last ayahs of {len(target)} rukus {dirc} from Juzz {start}"
                answers    = [max((a for a in filtered_sorted if a["ruku"]==r), key=lambda x:(x["surah"],x["ayah"])) for r in target]
            else:
                picks = random.sample(filtered_sorted, random.randint(KEYS_MIN, KEYS_MAX))
                keys  = [p["ayah_key"] for p in picks]
                content, answers = (f"Recite these ayahs: {', '.join(keys)}", picks)

            # include drill type in question dict
            qs.append({
                "content": content,
                "answers": answers,
                "type": drill,
            })

        st.session_state.questions = qs
        st.session_state.revealed   = {i: False for i in range(len(qs))}

# — Render questions & answers —
def render_question(i, q):
    key = f"q{i}"
    if key not in st.session_state.revealed:
        st.session_state.revealed[key] = False

    # map drill key to friendly label
    qtype = LABELS.get(q.get("type",""), q.get("type",""))
    with st.expander(f"Question {i+1} – {qtype}", expanded=True):
        st.markdown(
            f'<div style="text-align: center; margin-top: 0em; margin-bottom: 1.5em;">{q["content"]}</div>',
            unsafe_allow_html=True
        )
        cols = st.columns([2,1,2])
        with cols[1]:
            if st.button("Reveal Answer", key=f"btn_{i}"):
                st.session_state.revealed[key] = True

        if st.session_state.revealed[key]:
            st.markdown("---")
            for a in q["answers"]:
                html = f'<div dir="rtl" style="text-align: center; margin-bottom:1em;">'
                if include_info:
                    meta = f"Juzz {a['juzz']}, Ruku {a['ruku']}, Ayah {a['ayah_key']}"
                    html += f"<strong>{meta}</strong><br>{a['text']}"
                else:
                    html += f"{a['text']} - ({a['ayah_key']})"
                html += '</div>'
                st.markdown(html, unsafe_allow_html=True)

# — Display if questions exist —
if st.session_state.questions:
    st.markdown('<h2 style="text-align: center;">Your Challenge Questions</h2>', unsafe_allow_html=True)
    for idx, q in enumerate(st.session_state.questions):
        render_question(idx, q)
