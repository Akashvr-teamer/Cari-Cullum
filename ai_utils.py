"""Data loading + processing helpers for the CSE (AI&ML) curriculum explorer."""
import json
import os

import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

CAT_CONFIG = {
    "core": {"label": "Core / Compulsory", "color_var": "--gold", "emoji": "🟡"},
    "pe":   {"label": "Program Elective",  "color_var": "--teal", "emoji": "🔵"},
    "oe":   {"label": "Open Elective",     "color_var": "--coral", "emoji": "🟠"},
}


def load_courses():
    with open(os.path.join(DATA_DIR, "courses.json"), encoding="utf-8") as f:
        return json.load(f)


def load_semester_meta():
    with open(os.path.join(DATA_DIR, "semester_meta.json"), encoding="utf-8") as f:
        return json.load(f)


def bucket_of(course):
    prefix = course.get("category_prefix")
    if prefix == "PEC":
        return "pe"
    if prefix == "OEC":
        return "oe"
    return "core"  # PCC, PBC, UC, GA


def credit_value(course):
    credits = course.get("credits")
    if not credits:
        return 0.0
    if "/" in credits:
        parts = [float(p) for p in credits.split("/") if p.strip()]
        return min(parts) if parts else 0.0
    try:
        return float(credits)
    except ValueError:
        return 0.0


def by_semester(courses, sem):
    """Courses whose *primary, credit-bearing* semester is `sem`.

    This is the list the credit ruler/total is computed from. A course never
    counts twice here even if it's also cross-listed via semester_alt.
    """
    return [c for c in courses if c.get("semester_primary") == sem]


def cross_listed_for(courses, sem):
    """Courses taught in `sem` at *some* colleges, but whose official credit
    slot (semester_primary) is a different semester — e.g. Economics for
    Engineers / Engineering Ethics, which KTU lists as S3 but plenty of
    colleges actually run in S4.

    These are shown for reference in the alt semester's tab, but are
    deliberately excluded from that semester's credit_summary/total, since
    a student only takes — and is only credited for — it once, in whichever
    semester their own college schedules it.
    """
    return [c for c in courses if c.get("semester_alt") == sem]


def credit_summary(courses):
    core = 0.0
    pe_vals, oe_vals = set(), set()
    for c in courses:
        b = bucket_of(c)
        v = credit_value(c)
        if b == "core":
            core += v
        elif b == "pe":
            pe_vals.add(v)
        elif b == "oe":
            oe_vals.add(v)
    pe = min(pe_vals) if pe_vals else 0.0
    oe = min(oe_vals) if oe_vals else 0.0
    return {
        "core": core, "pe": pe, "oe": oe,
        "has_pe": bool(pe_vals), "has_oe": bool(oe_vals),
    }


@st.cache_data(show_spinner=False)
def condensed_catalog(courses, only_buckets=None, max_chars=None):
    """Build a compact, token-cheap text catalog for LLM context.

    Cached: with 98 courses this is cheap either way, but the chat tab calls
    it on every single message, so we skip rebuilding the string from
    scratch each time the course data itself hasn't changed.
    """
    lines = []
    for c in courses:
        b = bucket_of(c)
        if only_buckets and b not in only_buckets:
            continue
        label = CAT_CONFIG[b]["label"]
        line = f"[S{c.get('semester_primary')}] {c.get('code')} — {c.get('title')} ({label}, {c.get('credits')} cr)"
        prereq = c.get("prerequisites")
        if prereq and prereq.strip().lower() not in ("none", "nil", "-", ""):
            line += f" | Prereq: {prereq.strip()}"
        objectives = c.get("objectives") or []
        if objectives:
            line += f" | About: {objectives[0][:160]}"
        common_to = c.get("common_to")
        if common_to:
            line += f" | Common to: {common_to}"
        lines.append(line)
    text = "\n".join(lines)
    if max_chars and len(text) > max_chars:
        text = text[:max_chars] + "\n…(catalog truncated)"
    return text


def find_course(courses, code):
    code = (code or "").strip().upper()
    for c in courses:
        if c.get("code", "").upper() == code:
            return c
    return None
