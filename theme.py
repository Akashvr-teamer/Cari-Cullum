"""Liquid-glass theme + animated 'live wallpaper' CSS for the curriculum app.

Design intent: keep the original blueprint/navy identity (deep space navy,
gold/teal/coral accents, Newsreader+Inter+JetBrains Mono type system) and
layer a frosted-glass surface system on top, with a genuinely *live*
wallpaper behind it: drifting light sources, a slow aurora sweep, and a
twinkling star field — like glass panels on a drafting table catching
ambient light at night.

Two things this file is opinionated about, on purpose:
1. Mobile-first. Phones are the primary device this is tuned for; the
   desktop layout is the same markup, just with more breathing room.
2. Performance. `backdrop-filter` (the frosted-glass blur) is genuinely
   expensive to paint, and this app can render 30+ buttons on screen at
   once (course cards). So blur is reserved for a *handful* of large
   "hero" panels — header, ruler, outcomes, chat, sidebar — and stripped
   entirely from the many small repeated elements (course-card buttons),
   which instead get a cheap layered-gradient "glass" look with no blur.
   The live-wallpaper layers are pure box-shadow/gradient (no blur on
   mobile) for the same reason.
"""

import random


def _star_layer(n, seed, max_opacity):
    """Pre-bake a star field as one CSS box-shadow list (cheap: one paint,
    no per-star DOM nodes, no blur). Positions are in vw/vh so they scale
    naturally to any screen size, phone or desktop.
    """
    rnd = random.Random(seed)
    dots = []
    for _ in range(n):
        x = round(rnd.uniform(0, 100), 1)
        y = round(rnd.uniform(0, 100), 1)
        op = round(rnd.uniform(max_opacity * 0.45, max_opacity), 2)
        dots.append(f"{x}vw {y}vh rgba(234,241,251,{op})")
    return ",\n    ".join(dots)


_STARS_NEAR = _star_layer(55, 11, 0.85)
_STARS_MID = _star_layer(40, 22, 0.55)
_STARS_FAR = _star_layer(30, 33, 0.32)

CSS = f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600;6..72,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

<style>
:root{{
  --bg:#0c1825;
  --bg-deep:#081220;
  --grid-line: rgba(143,178,219,0.06);
  --ink:#eaf1fb;
  --ink-soft:#c4d3e8;
  --muted:#7e94b3;
  --muted-2:#5c7295;
  --rule: rgba(234,241,251,0.12);
  --rule-soft: rgba(234,241,251,0.07);
  --gold:#d9a441;
  --gold-soft: rgba(217,164,65,0.18);
  --teal:#52c7bd;
  --teal-soft: rgba(82,199,189,0.18);
  --coral:#e8896b;
  --coral-soft: rgba(232,137,107,0.18);
  --cross: #9fb2cc;
  --glass-bg: rgba(255,255,255,0.055);
  --glass-bg-strong: rgba(255,255,255,0.10);
  --glass-border: rgba(255,255,255,0.14);
  --glass-highlight: rgba(255,255,255,0.40);
  --radius-lg: 18px;
  --radius-md: 14px;
  --radius-sm: 10px;
  --font-display:'Newsreader', serif;
  --font-body:'Inter', sans-serif;
  --font-mono:'JetBrains Mono', monospace;
}}

*{{ -webkit-tap-highlight-color: transparent; }}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
  font-family: var(--font-body) !important;
  color: var(--ink) !important;
}}
h1, h2, h3, h4 {{ font-family: var(--font-display) !important; font-weight: 500 !important; letter-spacing: -0.01em; }}
code, pre, .stCodeBlock, [data-testid="stMarkdownContainer"] code {{ font-family: var(--font-mono) !important; }}

/* ---------- live wallpaper ---------- */
[data-testid="stAppViewContainer"]{{
  background:
    linear-gradient(var(--grid-line) 1px, transparent 1px) 0 0/40px 40px,
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px) 0 0/40px 40px,
    radial-gradient(120% 90% at 15% -10%, rgba(217,164,65,0.05), transparent 55%),
    radial-gradient(120% 90% at 90% 110%, rgba(82,199,189,0.05), transparent 55%),
    var(--bg) !important;
}}
[data-testid="stHeader"]{{ background: transparent !important; }}
[data-testid="stSidebar"]{{
  background: rgba(8,18,32,0.86) !important;
  backdrop-filter: blur(18px) saturate(140%);
  border-right: 1px solid var(--rule-soft);
}}
.block-container{{ padding-top: 1.1rem !important; padding-left: 1rem !important; padding-right: 1rem !important; max-width: 1180px; }}

.wallpaper-orbs{{ position: fixed; inset: 0; z-index: -3; overflow: hidden; pointer-events: none; }}
.orb{{ position: absolute; border-radius: 50%; filter: blur(90px); opacity: .30; will-change: transform; }}
.orb-gold{{ background: var(--gold); width: 480px; height: 480px; top: -12%; left: -8%; animation: driftA 46s ease-in-out infinite; }}
.orb-teal{{ background: var(--teal); width: 420px; height: 420px; bottom: -16%; right: -6%; animation: driftB 54s ease-in-out infinite; }}
.orb-coral{{ background: var(--coral); width: 320px; height: 320px; top: 38%; left: 58%; animation: driftC 62s ease-in-out infinite; }}
.orb-ghost{{ background: var(--ink); width: 260px; height: 260px; top: 62%; left: 18%; opacity: .07; animation: driftD 70s ease-in-out infinite; }}
@keyframes driftA{{ 0%,100%{{ transform: translate(0,0) scale(1);}} 50%{{ transform: translate(60px,40px) scale(1.12);}} }}
@keyframes driftB{{ 0%,100%{{ transform: translate(0,0) scale(1);}} 50%{{ transform: translate(-50px,-35px) scale(0.92);}} }}
@keyframes driftC{{ 0%,100%{{ transform: translate(0,0) scale(1);}} 50%{{ transform: translate(-35px,45px) scale(1.06);}} }}
@keyframes driftD{{ 0%,100%{{ transform: translate(0,0) scale(1);}} 50%{{ transform: translate(30px,-30px) scale(1.15);}} }}

/* aurora: a slow-rotating soft conic sweep — desktop-only (see media query) */
.wallpaper-aurora{{
  position: fixed; inset: -20%; z-index: -2; pointer-events: none;
  background: conic-gradient(from 0deg at 50% 50%,
    rgba(217,164,65,0.05), rgba(82,199,189,0.045), rgba(232,137,107,0.04),
    rgba(82,199,189,0.045), rgba(217,164,65,0.05));
  mix-blend-mode: screen;
  animation: auroraSpin 120s linear infinite;
  opacity: .6;
}}
@keyframes auroraSpin{{ to{{ transform: rotate(360deg); }} }}

/* stars: pure box-shadow dot fields, no blur, near-zero paint cost */
.wallpaper-stars{{ position: fixed; inset: 0; z-index: -1; pointer-events: none; }}
.star-layer{{ position:absolute; top:0; left:0; width:2px; height:2px; border-radius:50%; background:transparent; }}
.star-near{{ box-shadow: {_STARS_NEAR}; animation: twinkle 5.5s ease-in-out infinite; }}
.star-mid{{ box-shadow: {_STARS_MID}; animation: twinkle 7.5s ease-in-out infinite reverse; animation-delay: -2s; }}
.star-far{{ box-shadow: {_STARS_FAR}; animation: twinkle 9.5s ease-in-out infinite; animation-delay: -4s; }}
@keyframes twinkle{{ 0%,100%{{ opacity: .55; }} 50%{{ opacity: 1; }} }}

@media (prefers-reduced-motion: reduce){{
  .orb, .wallpaper-aurora, .star-near, .star-mid, .star-far{{ animation: none !important; }}
}}

/* lighter wallpaper on small screens: keep stars (cheap), drop aurora + shrink blur */
@media (max-width: 768px){{
  .wallpaper-aurora{{ display: none; }}
  .orb{{ filter: blur(46px); opacity: .22; }}
  .orb-ghost{{ display: none; }}
}}

/* ---------- glass surfaces ---------- */
.glass-panel{{
  background: linear-gradient(135deg, rgba(255,255,255,0.085), rgba(255,255,255,0.015));
  backdrop-filter: blur(20px) saturate(160%);
  -webkit-backdrop-filter: blur(20px) saturate(160%);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 10px 36px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.10);
  position: relative;
  padding: clamp(14px, 3.4vw, 22px) clamp(16px, 4vw, 26px);
  margin-bottom: 16px;
}}
.glass-panel::before{{
  content:''; position:absolute; top:0; left:14px; right:14px; height:1px;
  background: linear-gradient(90deg, transparent, var(--glass-highlight), transparent);
  opacity:.6;
}}
.glass-eyebrow{{ font-family: var(--font-mono); font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; color: var(--gold); margin-bottom:6px;}}

@media (max-width: 768px){{
  .glass-panel{{ backdrop-filter: blur(10px) saturate(150%); -webkit-backdrop-filter: blur(10px) saturate(150%); border-radius: var(--radius-md); }}
}}

/* header brand */
.brand-row{{ display:flex; align-items:baseline; justify-content:space-between; gap:18px; flex-wrap:wrap; }}
.brand-mark{{ font-family: var(--font-mono); font-size:11px; letter-spacing:.12em; color: var(--gold); border:1px solid var(--gold-soft); background: var(--gold-soft); padding:3px 8px; border-radius:4px; text-transform:uppercase; }}
.brand-title{{ font-family: var(--font-display); font-weight:600; font-size: clamp(21px, 4.6vw, 27px); margin: 7px 0 2px; line-height:1.15; }}
.brand-sub{{ font-family: var(--font-mono); font-size: clamp(10px, 2.6vw, 11.5px); color: var(--muted); }}
.brand-meta{{ font-family: var(--font-mono); font-size:11px; color: var(--muted-2); text-align:right; line-height:1.6; }}
@media (max-width: 560px){{
  .brand-meta{{ text-align:left; }}
}}

/* credit ruler */
.ruler-label{{ display:flex; justify-content:space-between; font-family: var(--font-mono); font-size:11px; color: var(--muted); margin-bottom:6px;}}
.ruler-label b{{ color: var(--ink-soft); }}
.ruler{{ height:20px; display:flex; border:1px solid var(--rule); border-radius:6px; overflow:hidden; }}
.ruler-seg{{ transition: width .4s ease; }}
.ruler-seg.core{{ background: var(--gold); }}
.ruler-seg.pe{{ background: var(--teal); }}
.ruler-seg.oe{{ background: var(--coral); }}
.ruler-note{{ font-size:11.5px; color: var(--muted); font-style: italic; margin-top:6px; }}

/* skills panel */
.skills-grid{{ display:grid; grid-template-columns: repeat(auto-fit, minmax(220px,1fr)); gap:8px 22px; margin-top:10px;}}
.skill-line{{ display:flex; gap:9px; font-size: clamp(12.5px, 3vw, 13.5px); line-height:1.55; color: var(--ink-soft); }}
.skill-line .si{{ font-family: var(--font-mono); color: var(--gold); font-size:11px; padding-top:3px; flex-shrink:0; }}

/* category group divider */
.cat-divider{{ display:flex; align-items:center; gap:12px; margin: 18px 0 6px; }}
.cat-divider .line{{ flex:1; height:1px; background: var(--rule-soft); }}
.cat-divider .label{{ font-family: var(--font-mono); font-size:12px; letter-spacing:.1em; text-transform:uppercase; color: var(--ink-soft); white-space:nowrap;}}
.cat-divider .count{{ color: var(--muted-2); font-weight:400; }}
.cat-divider.cross .label{{ color: var(--cross); }}

/* legend chips */
.legend-row{{ display:flex; gap:10px; flex-wrap:wrap; margin: 6px 0 4px; }}
.legend-chip{{ display:flex; align-items:center; gap:7px; font-family: var(--font-mono); font-size:11px; color: var(--muted); border:1px solid var(--rule-soft); padding:5px 10px; border-radius:20px; }}
.dot{{ width:8px; height:8px; border-radius:50%; display:inline-block; }}
.dot-core{{ background: var(--gold); }} .dot-pe{{ background: var(--teal); }} .dot-oe{{ background: var(--coral); }}
.dot-cross{{ width:8px; height:8px; border-radius:50%; border: 1.5px dashed var(--cross); background: transparent; }}

/* cross-listed note panel */
.cross-note{{ font-size: 12px; color: var(--muted); margin: -2px 0 10px; }}

/* ---------- stat grid (course detail) ---------- */
.stat-grid{{ display:grid; grid-template-columns: repeat(auto-fit, minmax(96px,1fr)); gap:8px; margin: 10px 0 6px; }}
.stat-chip{{ background: var(--glass-bg); border:1px solid var(--glass-border); border-radius: var(--radius-sm); padding: 9px 12px; }}
.stat-chip .stat-label{{ font-family: var(--font-mono); font-size:10px; letter-spacing:.08em; text-transform:uppercase; color: var(--muted); margin-bottom:3px; }}
.stat-chip .stat-value{{ font-size: 16px; font-weight:600; color: var(--ink); }}

/* ---------- buttons as glass course cards ---------- */
div[data-testid="stButton"] button{{
  width: 100%;
  text-align: left;
  white-space: pre-line;
  background: linear-gradient(135deg, rgba(255,255,255,0.075), rgba(255,255,255,0.02)) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
  color: var(--ink) !important;
  padding: 14px 16px !important;
  min-height: 44px;
  line-height: 1.5;
  transition: transform .15s ease, background .15s ease, border-color .15s ease;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
}}
div[data-testid="stButton"] button:hover{{
  transform: translateY(-2px);
  background: linear-gradient(135deg, rgba(255,255,255,0.13), rgba(255,255,255,0.035)) !important;
  border-color: rgba(255,255,255,0.32) !important;
}}
div[data-testid="stButton"] button:active{{ transform: translateY(0); }}
div[data-testid="stButton"] button p{{ font-size: 13.5px !important; }}

/* category-tinted left edge via container key (Streamlit st.container(key=...)) */
div[class*="st-key-card_core_"] div[data-testid="stButton"] button{{ border-left: 3px solid var(--gold) !important; }}
div[class*="st-key-card_pe_"]   div[data-testid="stButton"] button{{ border-left: 3px solid var(--teal) !important; }}
div[class*="st-key-card_oe_"]   div[data-testid="stButton"] button{{ border-left: 3px solid var(--coral) !important; }}
div[class*="st-key-card_cross_"] div[data-testid="stButton"] button{{ border-left: 3px dashed var(--cross) !important; opacity: .92; }}

/* sidebar + generic buttons (AI tabs) keep a calmer style */
section[data-testid="stSidebar"] div[data-testid="stButton"] button{{ border-left: none !important; }}

/* tabs */
button[data-baseweb="tab"]{{ font-family: var(--font-mono) !important; font-size: 12px !important; padding: 8px 10px !important; }}
div[data-testid="stTabs"] [data-baseweb="tab-list"]{{
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  border: 1px solid var(--rule-soft);
  padding: 4px;
  overflow-x: auto;
}}

/* chat */
[data-testid="stChatMessage"]{{
  background: var(--glass-bg) !important;
  backdrop-filter: blur(12px);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-md);
}}
[data-testid="stChatInput"] textarea{{ background: var(--glass-bg) !important; }}

/* misc form widgets */
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input, .stSelectbox div[data-baseweb="select"]{{
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--ink) !important;
}}
[data-testid="stExpander"]{{
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: var(--radius-md) !important;
}}

/* scrollbar (desktop) */
::-webkit-scrollbar{{ width: 10px; height: 10px; }}
::-webkit-scrollbar-track{{ background: transparent; }}
::-webkit-scrollbar-thumb{{ background: rgba(234,241,251,0.14); border-radius: 8px; }}
::-webkit-scrollbar-thumb:hover{{ background: rgba(234,241,251,0.24); }}

footer{{ font-family: var(--font-mono); font-size: 11px; color: var(--muted-2); }}
hr{{ border-color: var(--rule-soft) !important; }}
::selection{{ background: var(--gold-soft); color: var(--ink); }}

/* ---------- broad mobile tightening ---------- */
@media (max-width: 768px){{
  .block-container{{ padding-top: .8rem !important; }}
  .skills-grid{{ grid-template-columns: 1fr; }}
  .legend-row{{ gap: 6px; }}
  .legend-chip{{ font-size: 10px; padding: 4px 8px; }}
  [data-testid="stSidebar"]{{ backdrop-filter: blur(10px) saturate(140%); }}
}}
</style>

<div class="wallpaper-orbs">
  <div class="orb orb-gold"></div>
  <div class="orb orb-teal"></div>
  <div class="orb orb-coral"></div>
  <div class="orb orb-ghost"></div>
</div>
<div class="wallpaper-aurora"></div>
<div class="wallpaper-stars">
  <div class="star-layer star-far"></div>
  <div class="star-layer star-mid"></div>
  <div class="star-layer star-near"></div>
</div>
"""


def inject(st):
    st.markdown(CSS, unsafe_allow_html=True)
