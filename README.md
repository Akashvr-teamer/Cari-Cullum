# CSE (AI & ML) Curriculum Explorer

A Streamlit rebuild of your curriculum site: same S3–S8 course map, plus an AI
chat advisor, an AI elective finder, a "liquid glass" interface, and a live,
twinkling-star wallpaper. Free to run and free to host — and tuned to feel
fast and natural on a phone, since that's where most people will actually
open it.

## What's inside

- `app.py` — the whole app (UI, tabs, course modal)
- `theme.py` — the glass + wallpaper CSS, injected into the page
- `data_utils.py` — loads/processes `data/courses.json` and `data/semester_meta.json`,
  including the S3/S4 cross-listing logic (see below)
- `ai_utils.py` — thin wrapper around Groq and Google Gemini's free APIs
- `data/` — your 98 courses + semester outcomes, extracted from the original HTML
- `.streamlit/config.toml` — dark base theme
- `.streamlit/secrets.toml.example` — template for API keys

## Run it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

It opens at `http://localhost:8501`. The curriculum map (Tab 1) works
immediately with no setup — it's just your data. The two AI tabs need a free
API key (see below), entered in the sidebar.

## Getting a free AI key (no credit card)

Pick **one**:

- **Groq** (fast, open-weight models like Llama 3.3): sign up at
  [console.groq.com](https://console.groq.com), create a key, paste it into
  the sidebar.
- **Google Gemini**: sign up at
  [aistudio.google.com](https://aistudio.google.com), create a key, paste it
  into the sidebar.

Both have generous free daily limits as of mid-2026 — plenty for personal use.
If a request ever fails with a model-not-found error, open **Advanced: model
name** in the sidebar and swap in whatever model your provider's console
currently lists as free (free-tier model names get renamed/retired every
several months on both platforms).

### Making it stop asking for your key every time

Pasting the key into the sidebar only keeps it for your current browser
session — Streamlit forgets it on the next page reload or app restart, which
is the repeat-prompt you were hitting. Fix it once:

- **Locally** — copy `secrets.toml.example` to `.streamlit/secrets.toml`
  (create the `.streamlit/` folder if it doesn't exist) and fill in your key.
  It's already in `.gitignore`, so it won't get committed.
- **On Streamlit Community Cloud** — open your deployed app → **Settings →
  Secrets** and paste the same `GROQ_API_KEY = "..."` line there.

Either way, the sidebar now detects the secret automatically, shows a
"✓ loaded from saved secrets" badge instead of an input box, and never asks
again — for you or anyone else who opens the app.

## Hosting it for free — Streamlit Community Cloud

1. **Put this folder in a GitHub repo.**
   - Create a free GitHub account if you don't have one.
   - Create a new repository (public or private both work).
   - Upload this whole `app/` folder's contents to the repo root (or push via
     `git init && git add . && git commit -m "init" && git push`).
   - `.streamlit/secrets.toml` is git-ignored on purpose — never commit real
     API keys.

2. **Deploy.**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in with
     GitHub.
   - Click **New app**, pick your repo/branch, set the main file path to
     `app.py`, and deploy.
   - It builds from `requirements.txt` automatically. First build takes a
     couple of minutes.

3. **Add your AI key as a secret (so visitors don't need their own).**
   - In your deployed app, open **Settings → Secrets**.
   - Paste:
     ```toml
     GROQ_API_KEY = "gsk_your_key_here"
     GEMINI_API_KEY = "AIza_your_key_here"
     ```
   - Save. The app reads these automatically and pre-fills the sidebar — you
     can include one or both.

4. **Done.** Your app is live for free at `https://<your-app-name>.streamlit.app`,
   with no spend cap and no traffic-based billing on the Community Cloud tier.

If you'd rather not expose your own key to every visitor, leave secrets empty
and let each person paste their own free key in the sidebar — it's only kept
for their session.

## Notes on the AI features

- **Ask the Curriculum** (chat) and **Elective Finder** both work by sending
  a compact, plain-text version of your course catalog (~5k tokens for all 98
  courses) to the model as context, and instructing it to answer only from
  that data. This keeps cost at $0 on free tiers and keeps answers grounded
  in your actual syllabus extract rather than the model's general knowledge.
- Nothing about your data is sent anywhere except to whichever AI provider
  you choose, only when you use the AI tabs.

## A note on Economics / Engineering Ethics (S3 vs S4)

KTU's syllabus lists **Economics for Engineers** and **Engineering Ethics &
Sustainable Development** under S3, but a lot of colleges actually run them
in S4 instead. The explorer now shows both courses normally in S3, *and* as
a clearly marked "🔁 cross-listed" card (dashed border) in S4 for reference —
but only counts their credits once, toward S3's total, so S4's credit ruler
doesn't get inflated. If your college runs them in S4, just mentally shift
those 4 credits over; nothing else in the data model changes.

## Performance & mobile

- Each tab (Curriculum Map, Ask the Curriculum, Elective Finder) is its own
  Streamlit **fragment**. Typing in the chat or clicking "Find electives"
  only reruns that tab — it no longer has to rebuild the entire 98-course
  grid on every keystroke, which was the main source of lag.
- The frosted-glass blur (`backdrop-filter`) is reserved for a handful of
  large panels (header, ruler, outcomes, chat, sidebar). The 90+ course-card
  buttons use a cheap layered-gradient look instead — blur on that many
  small elements is what actually bogs phones down.
- The wallpaper is mostly CSS-only (orbs, a slow aurora sweep, and a
  twinkling star field built from `box-shadow`, not separate DOM nodes), and
  the heavier bits (aurora, full-strength blur) are dialled back automatically
  on screens under 768px to save battery and stay smooth.
- Layout is mobile-first: course-card grids and metric chips reflow to a
  single column on a phone, type sizes scale fluidly with the viewport, and
  the sidebar collapses by default on small screens.

## Customizing the look

`theme.py` holds all the CSS in one place:
- Color tokens (`--gold`, `--teal`, `--coral`, `--cross`, `--bg`, etc.) at the top.
- `.wallpaper-orbs` / `.orb` / `@keyframes drift*` control the drifting light
  orbs; `.wallpaper-aurora` is the slow rotating color sweep; `.wallpaper-stars`
  / `_star_layer()` (top of the file) control the twinkling star field — bump
  `n` or the seed in `_star_layer()` calls to change density/pattern.
- `.glass-panel` and the `stButton` rules control the liquid-glass surfaces.
- The `@media (max-width: 768px)` blocks near the bottom control the mobile-
  specific tweaks (lighter blur, single-column grids, etc).

If a future Streamlit version changes its internal HTML structure, some
`[data-testid="..."]` selectors in `theme.py` may need updating — the app
still works either way, just with less of the glass styling applied.
