import streamlit as st

import theme
from data_utils import (
    CAT_CONFIG, load_courses, load_semester_meta, bucket_of,
    by_semester, cross_listed_for, credit_summary, condensed_catalog, find_course,
)
from ai_utils import call_llm, LLMError, DEFAULT_MODELS

st.set_page_config(
    page_title="CSE (AI & ML) · Curriculum Explorer",
    page_icon="🧊",
    layout="wide",
)
theme.inject(st)

# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_data():
    return load_courses(), load_semester_meta()

COURSES, SEMESTER_META = get_data()
SEMESTERS = sorted(SEMESTER_META.keys(), key=int)

# ----------------------------------------------------------------------------
# Sidebar — AI provider config (free tiers: Groq / Google Gemini)
#
# API keys are resolved secrets-first: if GROQ_API_KEY / GEMINI_API_KEY is
# set as a Streamlit secret, the sidebar never asks at all. Only falls back
# to a manual text input — kept for the current browser session only — when
# no secret is configured.
# ----------------------------------------------------------------------------
SECRET_NAMES = {"Groq": "GROQ_API_KEY", "Gemini": "GEMINI_API_KEY"}


def _get_secret(name):
    """st.secrets.get() raises StreamlitSecretNotFoundError instead of
    returning the default when *no* secrets.toml exists anywhere yet
    (a fresh checkout, before anyone's set one up) — which would otherwise
    crash the whole app before the sidebar even renders. Treat "no secrets
    configured" as just... no secret.
    """
    try:
        return st.secrets.get(name, "")
    except Exception:
        return ""


with st.sidebar:
    st.markdown("### 🤖 AI setup")
    st.caption("Powers the **Ask the Curriculum** and **Elective Finder** tabs. Free tier, no card needed.")

    provider = st.radio("Provider", ["Groq", "Gemini"], horizontal=True, key="provider")
    state_key = f"key_{provider}"
    secret_val = _get_secret(SECRET_NAMES[provider])

    if secret_val:
        st.session_state[state_key] = secret_val
        st.success("API key loaded from saved secrets — nothing to type.", icon="🔐")
    else:
        st.session_state.setdefault(state_key, "")
        st.text_input(
            f"{provider} API key",
            type="password",
            key=state_key,
            help="Kept only for this browser session — it'll be gone after a page reload or "
                 "app restart unless you save it as a secret (see below).",
        )
        if not st.session_state[state_key]:
            with st.expander("🔒 Stop being asked every time"):
                st.markdown(
                    "Streamlit forgets anything typed into this box the moment the page "
                    "reloads or the app restarts — that's the repeat prompt you're hitting. "
                    "Fix it once, for good:\n\n"
                    "**Running locally** — create `.streamlit/secrets.toml` next to `app.py` "
                    "(there's a `secrets.toml.example` template included) with:\n"
                    f"```toml\n{SECRET_NAMES[provider]} = \"your_key_here\"\n```\n\n"
                    "**Deployed on Streamlit Community Cloud** — open your app, go to "
                    "**Settings → Secrets**, and paste the same line there.\n\n"
                    "Either way, this sidebar auto-detects it next load and stops asking."
                )

    with st.expander("Advanced: model name"):
        st.text_input("Model", value=DEFAULT_MODELS[provider], key=f"model_{provider}")
        st.caption("Free-tier model names change occasionally — update here if a request fails.")

    if provider == "Groq":
        st.caption("Get a free key → [console.groq.com](https://console.groq.com)")
    else:
        st.caption("Get a free key → [aistudio.google.com](https://aistudio.google.com)")

    st.divider()
    st.caption("Built with Streamlit · deployable free on Streamlit Community Cloud")

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="glass-panel">
      <div class="brand-row">
        <div>
          <span class="brand-mark">KTU · 2024 Scheme</span>
          <div class="brand-title">CSE <span style="color:var(--muted)">·</span> AI &amp; ML</div>
          <div class="brand-sub">Curriculum Explorer — S3 to S8 · Live wallpaper · Liquid glass UI</div>
        </div>
        <div class="brand-meta">{len(COURSES)} courses indexed<br>{len(SEMESTERS)} semesters · S3–S8</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("📋 Reading this map (disclaimer)"):
    st.markdown(
        "This explorer is built directly from a syllabus copy PDF — every course code, credit value, "
        "module and outcome is parsed from that document. It doesn't include the master scheme table, so "
        "three things aren't reflected automatically: **(1)** how many electives must be picked per basket "
        "(shown as *pick 1* by convention), **(2)** non-syllabus credit slots like Major Project, Mini "
        "Project, Internship or Seminar, and **(3)** which semester a couple of cross-listed courses (like "
        "Economics for Engineers / Engineering Ethics) actually run in at *your* college — KTU lists them "
        "under S3, but many colleges schedule them in S4 instead, so they're shown in both tabs here and "
        "counted only once. Cross-check all of this against your department's official curriculum structure "
        "sheet. The AI tabs answer **only** from this same extracted data — they can't see anything outside it."
    )

tab_curriculum, tab_chat, tab_finder = st.tabs(["📚 Curriculum Map", "💬 Ask the Curriculum", "🎯 Elective Finder"])

# ----------------------------------------------------------------------------
# Tab 1 — Curriculum map
#
# Wrapped as a single @st.fragment: clicking a filter or a course card only
# reruns this block, not the AI chat history or the rest of the app — and,
# just as important, typing in the chat tab no longer has to rebuild this
# entire 98-course grid on every keystroke either.
# ----------------------------------------------------------------------------
@st.fragment
def render_curriculum_tab():
    st.markdown(
        """
        <div class="legend-row">
          <div class="legend-chip"><span class="dot dot-core"></span>Core / Compulsory</div>
          <div class="legend-chip"><span class="dot dot-pe"></span>Program Elective</div>
          <div class="legend-chip"><span class="dot dot-oe"></span>Open Elective</div>
          <div class="legend-chip"><span class="dot-cross"></span>Cross-listed (alt. semester)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    sem_tabs = st.tabs([f"S{s}" for s in SEMESTERS])

    for sem, sem_tab in zip(SEMESTERS, sem_tabs):
        with sem_tab:
            meta = SEMESTER_META[sem]
            courses = by_semester(COURSES, sem)
            cross_listed = cross_listed_for(COURSES, sem)
            cs = credit_summary(courses)
            total = cs["core"] + cs["pe"] + cs["oe"]
            core_pct = (cs["core"] / total * 100) if total else 0
            pe_pct = (cs["pe"] / total * 100) if total else 0
            oe_pct = (cs["oe"] / total * 100) if total else 0
            pick_note = []
            if cs["has_pe"]:
                pick_note.append("1 Program Elective")
            if cs["has_oe"]:
                pick_note.append("1 Open Elective")
            note = ("picking " + " + ".join(pick_note)) if pick_note else "core only — see note above"

            col1, col2 = st.columns([2.1, 1])
            with col1:
                st.markdown(
                    f"""<div class="glass-panel">
                          <div class="glass-eyebrow">Semester {sem} · {meta['theme']}</div>
                          <h3 style="margin:0;">{meta['blurb']}</h3>
                        </div>""",
                    unsafe_allow_html=True,
                )
            with col2:
                segs = ""
                if cs["core"]:
                    segs += f"<div class='ruler-seg core' style='width:{core_pct:.2f}%'></div>"
                if cs["pe"]:
                    segs += f"<div class='ruler-seg pe' style='width:{pe_pct:.2f}%'></div>"
                if cs["oe"]:
                    segs += f"<div class='ruler-seg oe' style='width:{oe_pct:.2f}%'></div>"
                st.markdown(
                    f"""<div class="glass-panel">
                          <div class="ruler-label"><span>Min. credit load*</span><b>{total:g} cr</b></div>
                          <div class="ruler">{segs}</div>
                          <div class="ruler-note">*{note}</div>
                        </div>""",
                    unsafe_allow_html=True,
                )

            skills_html = "".join(f"<div class='skill-line'><span class='si'>▸</span><span>{s}</span></div>" for s in meta["skills"])
            st.markdown(
                f"""<div class="glass-panel">
                      <div class="glass-eyebrow">Outcomes</div>
                      <h4 style="margin:4px 0 6px;font-style:italic;">What you should be able to do after Semester {sem}</h4>
                      <div class="skills-grid">{skills_html}</div>
                    </div>""",
                unsafe_allow_html=True,
            )

            bucket_options = {"core": "Core / Compulsory", "pe": "Program Elective", "oe": "Open Elective"}
            selected_buckets = st.multiselect(
                "Filter",
                options=list(bucket_options.keys()),
                default=list(bucket_options.keys()),
                format_func=lambda k: bucket_options[k],
                key=f"filter_{sem}",
                label_visibility="collapsed",
            )

            for bucket in ["core", "pe", "oe"]:
                if bucket not in selected_buckets:
                    continue
                group = [c for c in courses if bucket_of(c) == bucket]
                if not group:
                    continue
                cfg = CAT_CONFIG[bucket]
                st.markdown(
                    f"""<div class="cat-divider">
                          <span class="dot dot-{bucket}"></span>
                          <span class="label">{cfg['label']} <span class="count">({len(group)})</span></span>
                          <div class="line"></div>
                        </div>""",
                    unsafe_allow_html=True,
                )
                if bucket == "pe":
                    st.caption("Program Elective basket — typically pick one course from this group.")
                if bucket == "oe":
                    st.caption("Open Elective basket — typically pick one, often shared across CSE-family branches.")

                cols = st.columns(3)
                for i, c in enumerate(group):
                    with cols[i % 3]:
                        with st.container(key=f"card_{bucket}_{sem}_{c['code']}"):
                            alt_tag = f"  ·  may run in S{c['semester_alt']} too" if c.get("semester_alt") else ""
                            label = (
                                f"{cfg['emoji']} `{c.get('code','—')}`  ·  {c.get('credits','—')} cr  \n"
                                f"**{c.get('title','Untitled')}**  \n"
                                f"{c.get('course_type') or '—'}{alt_tag}  ·  view syllabus →"
                            )
                            if st.button(label, key=f"btn_{bucket}_{sem}_{c['code']}", use_container_width=True):
                                st.session_state.selected_course = c["code"]
                                st.rerun()

            if cross_listed:
                st.markdown(
                    """<div class="cat-divider cross">
                          <span class="dot-cross"></span>
                          <span class="label">Cross-listed here too</span>
                          <div class="line"></div>
                        </div>""",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    "<div class='cross-note'>Officially scheduled in a different semester, but plenty of "
                    "colleges run it here instead — it depends on your institution. It's already counted "
                    "toward that other semester's credit load above, so it's <b>not</b> added to this "
                    "semester's total too, to avoid double-counting.</div>",
                    unsafe_allow_html=True,
                )
                cols = st.columns(3)
                for i, c in enumerate(cross_listed):
                    with cols[i % 3]:
                        with st.container(key=f"card_cross_{sem}_{c['code']}"):
                            label = (
                                f"🔁 `{c.get('code','—')}`  ·  {c.get('credits','—')} cr  \n"
                                f"**{c.get('title','Untitled')}**  \n"
                                f"usually S{c.get('semester_primary')}  ·  view syllabus →"
                            )
                            if st.button(label, key=f"btn_cross_{sem}_{c['code']}", use_container_width=True):
                                st.session_state.selected_course = c["code"]
                                st.rerun()


with tab_curriculum:
    render_curriculum_tab()


def render_course_detail(c):
    bucket = bucket_of(c)
    cfg = CAT_CONFIG[bucket]
    badges = f"**{cfg['label']}**"
    if c.get("course_type"):
        badges += f" · {c['course_type']}"
    if c.get("common_to"):
        badges += f" · Common to {c['common_to']}"
    st.caption(badges)
    st.markdown(f"### {c.get('title','Untitled')}")
    sem_line = f"{c.get('code','—')} · Semester S{c.get('semester_primary')}"
    if c.get("semester_alt"):
        sem_line += f" (some colleges: S{c['semester_alt']})"
    st.caption(sem_line)

    stats = [
        ("Credits", c.get("credits") or "—"),
        ("L:T:P:R", c.get("ltpr") or "—"),
        ("CIE", c.get("cie") or "—"),
        ("ESE", c.get("ese") or "—"),
        ("Exam dur.", c.get("exam_hours") or "—"),
    ]
    chips_html = "".join(
        f"<div class='stat-chip'><div class='stat-label'>{lab}</div><div class='stat-value'>{val}</div></div>"
        for lab, val in stats
    )
    st.markdown(f"<div class='stat-grid'>{chips_html}</div>", unsafe_allow_html=True)

    if c.get("prerequisites") and c["prerequisites"].strip().lower() not in ("none", "nil", "-", ""):
        st.caption(f"**Prerequisites:** {c['prerequisites']}")

    if c.get("objectives"):
        st.markdown("**Course objectives**")
        for o in c["objectives"]:
            st.markdown(f"- {o}")

    if c.get("modules"):
        is_lab = c.get("syllabus_type") == "experiments"
        st.markdown(f"**{'Lab experiments' if is_lab else 'Syllabus modules'}**")
        for m in c["modules"]:
            tag = f"#{m['id']}" if is_lab else f"Module {m['id']}"
            hrs = f" · {m['trail']} hrs" if m.get("trail") else ""
            st.markdown(f"**{tag}**{hrs}  \n{m.get('desc') or '—'}")
            st.markdown("---")

    if c.get("course_outcomes"):
        st.markdown("**Course outcomes**")
        for co in c["course_outcomes"]:
            st.markdown(f"- `{co['id']}` ({co.get('level','—')}) — {co.get('desc','—')}")

    if not (c.get("objectives") or c.get("modules") or c.get("course_outcomes")):
        st.caption("No further syllabus detail was extractable for this course.")


@st.dialog("Course syllabus", width="large")
def course_dialog():
    code = st.session_state.get("selected_course")
    course = find_course(COURSES, code)
    if st.button("✕ Close"):
        st.session_state.selected_course = None
        st.rerun()
    if not course:
        st.write("Course not found.")
        return
    render_course_detail(course)


if st.session_state.get("selected_course"):
    course_dialog()

# ----------------------------------------------------------------------------
# Tab 2 — Ask the Curriculum (AI chat)
# ----------------------------------------------------------------------------
@st.fragment
def render_chat_tab():
    st.caption(
        "Ask about prerequisites, what a course covers, how semesters compare, or anything else in this "
        "syllabus extract. The assistant only answers from the catalog below — it won't make things up about "
        "courses it doesn't have data for."
    )
    st.session_state.setdefault("chat_messages", [])

    for m in st.session_state.chat_messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    prompt = st.chat_input("e.g. What are the prerequisites for Deep Learning Concepts?")
    if prompt:
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Reading the syllabus…"):
                system_prompt = (
                    "You are a precise, friendly curriculum advisor for the KTU B.Tech CSE (AI & ML) "
                    "programme, 2024 scheme, semesters S3 to S8. Answer ONLY using the catalog data below — "
                    "never invent course content, credits, or prerequisites that aren't in it. If asked about "
                    "something outside this data (other semesters, fees, admissions, faculty, etc.), say "
                    "plainly that it's outside this syllabus extract. Always mention course codes when you "
                    "reference a course. Keep answers concise and use markdown formatting.\n\n"
                    f"CATALOG:\n{condensed_catalog(COURSES)}"
                )
                try:
                    reply = call_llm(
                        provider=st.session_state.provider,
                        api_key=st.session_state.get(f"key_{st.session_state.provider}"),
                        system_prompt=system_prompt,
                        user_prompt=prompt,
                        model=st.session_state.get(f"model_{st.session_state.provider}"),
                        history=st.session_state.chat_messages[:-1][-12:],
                    )
                except LLMError as e:
                    reply = f"⚠️ {e}"
            st.markdown(reply)
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})

    if st.session_state.chat_messages and st.button("Clear conversation"):
        st.session_state.chat_messages = []
        st.rerun(scope="fragment")


with tab_chat:
    render_chat_tab()

# ----------------------------------------------------------------------------
# Tab 3 — Elective Finder (AI recommendations)
# ----------------------------------------------------------------------------
@st.fragment
def render_finder_tab():
    st.caption(
        "Describe your interests or goals — the AI scans every Program Elective and Open Elective in this "
        "catalog and recommends the ones that fit best, with reasoning tied to what's actually in the syllabus."
    )
    interests = st.text_area(
        "What are you interested in, or what do you want to be able to do?",
        placeholder="e.g. I like NLP and want to go into applied research… / I enjoy systems-level programming and security… / I want something practical for a startup idea…",
        height=100,
    )
    sem_filter = st.selectbox("Limit to a semester (optional)", ["Any semester"] + [f"S{s}" for s in SEMESTERS])

    if st.button("✨ Find electives", type="primary"):
        if not interests.strip():
            st.warning("Tell it a bit about your interests first.")
        else:
            with st.spinner("Scanning electives…"):
                elective_pool = COURSES
                if sem_filter != "Any semester":
                    elective_pool = by_semester(COURSES, sem_filter[1:])
                catalog = condensed_catalog(elective_pool, only_buckets={"pe", "oe"})
                system_prompt = (
                    "You are an elective-recommendation assistant for the KTU B.Tech CSE (AI & ML) programme, "
                    "2024 scheme. You are given a catalog of Program Electives (PE) and Open Electives (OE) "
                    "only. Based on the student's stated interests, recommend the 4-6 best-fitting electives. "
                    "For each: bold the course code and title, note its semester, and give one or two sentences "
                    "of reasoning grounded in the catalog's 'About' / prerequisite info — don't invent syllabus "
                    "content not present below. Group or order by relevance. Use markdown.\n\n"
                    f"ELECTIVE CATALOG:\n{catalog}"
                )
                try:
                    reply = call_llm(
                        provider=st.session_state.provider,
                        api_key=st.session_state.get(f"key_{st.session_state.provider}"),
                        system_prompt=system_prompt,
                        user_prompt=f"My interests/goals: {interests}",
                        model=st.session_state.get(f"model_{st.session_state.provider}"),
                    )
                    st.markdown(reply)
                except LLMError as e:
                    st.error(str(e))


with tab_finder:
    render_finder_tab()

st.markdown(
    "<footer>Generated from the uploaded KTU CSE (AI&ML) syllabus copy · Course Outcomes coded K1–K6 per "
    "Bloom's Taxonomy · Reference only, not an official record.</footer>",
    unsafe_allow_html=True,
)
