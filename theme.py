"""Liquid-glass theme + animated 'live wallpaper' CSS for the curriculum app.

Design intent: keep the original blueprint/navy identity (deep space navy,
gold/teal/coral accents, Newsreader+Inter+JetBrains Mono type system) and
layer a frosted-glass surface system on top, with three slow-drifting,
blurred light sources behind it standing in for a "live wallpaper" —
like glass panels on a drafting table catching ambient light at night.
"""

CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600;6..72,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

<style>
:root{
  --bg:#0c1825;
  --bg-deep:#081220;
  --grid-line: rgba(143,178,219,0.07);
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
  --glass-bg: rgba(255,255,255,0.055);
  --glass-bg-strong: rgba(255,255,255,0.10);
  --glass-border: rgba(255,255,255,0.14);
  --glass-highlight: rgba(255,255,255,0.40);
  --font-display:'Newsreader', serif;
  --font-body:'Inter', sans-serif;
  --font-mono:'JetBrains Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
  font-family: var(--font-body) !important;
  color: var(--ink) !important;
}
h1, h2, h3, h4 { font-family: var(--font-display) !important; font-weight: 500 !important; letter-spacing: -0.01em; }
code, pre, .stCodeBlock, [data-testid="stMarkdownContainer"] code { font-family: var(--font-mono) !important; }

/* ---------- live wallpaper ---------- */
[data-testid="stAppViewContainer"]{
  background:
    linear-gradient(var(--grid-line) 1px, transparent 1px) 0 0/40px 40px,
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px) 0 0/40px 40px,
    var(--bg) !important;
}
[data-testid="stHeader"]{ background: transparent !important; }
[data-testid="stSidebar"]{
  background: rgba(8,18,32,0.78) !important;
  backdrop-filter: blur(18px) saturate(140%);
  border-right: 1px solid var(--rule-soft);
}
.block-container{ padding-top: 1.6rem !important; max-width: 1180px; }

.wallpaper-orbs{ position: fixed; inset: 0; z-index: -1; overflow: hidden; pointer-events: none; }
.orb{ position: absolute; border-radius: 50%; filter: blur(90px); opacity: .30; will-change: transform; }
.orb-gold{ background: var(--gold); width: 480px; height: 480px; top: -12%; left: -8%; animation: driftA 42s ease-in-out infinite; }
.orb-teal{ background: var(--teal); width: 420px; height: 420px; bottom: -16%; right: -6%; animation: driftB 50s ease-in-out infinite; }
.orb-coral{ background: var(--coral); width: 320px; height: 320px; top: 38%; left: 58%; animation: driftC 58s ease-in-out infinite; }
@keyframes driftA{ 0%,100%{ transform: translate(0,0) scale(1);} 50%{ transform: translate(60px,40px) scale(1.12);} }
@keyframes driftB{ 0%,100%{ transform: translate(0,0) scale(1);} 50%{ transform: translate(-50px,-35px) scale(0.92);} }
@keyframes driftC{ 0%,100%{ transform: translate(0,0) scale(1);} 50%{ transform: translate(-35px,45px) scale(1.06);} }
@media (prefers-reduced-motion: reduce){ .orb{ animation: none !important; } }

/* ---------- glass surfaces ---------- */
.glass-panel{
  background: linear-gradient(135deg, rgba(255,255,255,0.085), rgba(255,255,255,0.015));
  backdrop-filter: blur(22px) saturate(160%);
  -webkit-backdrop-filter: blur(22px) saturate(160%);
  border: 1px solid var(--glass-border);
  border-radius: 18px;
  box-shadow: 0 10px 36px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.10);
  position: relative;
  padding: 20px 24px;
  margin-bottom: 18px;
}
.glass-panel::before{
  content:''; position:absolute; top:0; left:14px; right:14px; height:1px;
  background: linear-gradient(90deg, transparent, var(--glass-highlight), transparent);
  opacity:.6;
}
.glass-eyebrow{ font-family: var(--font-mono); font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; color: var(--gold); margin-bottom:6px;}

/* header brand */
.brand-row{ display:flex; align-items:baseline; justify-content:space-between; gap:18px; flex-wrap:wrap; }
.brand-mark{ font-family: var(--font-mono); font-size:11px; letter-spacing:.12em; color: var(--gold); border:1px solid var(--gold-soft); background: var(--gold-soft); padding:3px 8px; border-radius:4px; text-transform:uppercase; }
.brand-title{ font-family: var(--font-display); font-weight:600; font-size:26px; margin: 6px 0 2px; }
.brand-sub{ font-family: var(--font-mono); font-size:11.5px; color: var(--muted); }
.brand-meta{ font-family: var(--font-mono); font-size:11px; color: var(--muted-2); text-align:right; line-height:1.6; }

/* credit ruler */
.ruler-label{ display:flex; justify-content:space-between; font-family: var(--font-mono); font-size:11px; color: var(--muted); margin-bottom:6px;}
.ruler-label b{ color: var(--ink-soft); }
.ruler{ height:20px; display:flex; border:1px solid var(--rule); border-radius:6px; overflow:hidden; }
.ruler-seg.core{ background: var(--gold); }
.ruler-seg.pe{ background: var(--teal); }
.ruler-seg.oe{ background: var(--coral); }
.ruler-note{ font-size:11.5px; color: var(--muted); font-style: italic; margin-top:6px; }

/* skills panel */
.skills-grid{ display:grid; grid-template-columns: repeat(auto-fit, minmax(230px,1fr)); gap:8px 22px; margin-top:10px;}
.skill-line{ display:flex; gap:9px; font-size:13.5px; line-height:1.55; color: var(--ink-soft); }
.skill-line .si{ font-family: var(--font-mono); color: var(--gold); font-size:11px; padding-top:3px; flex-shrink:0; }

/* category group divider */
.cat-divider{ display:flex; align-items:center; gap:12px; margin: 18px 0 6px; }
.cat-divider .line{ flex:1; height:1px; background: var(--rule-soft); }
.cat-divider .label{ font-family: var(--font-mono); font-size:12px; letter-spacing:.1em; text-transform:uppercase; color: var(--ink-soft); white-space:nowrap;}
.cat-divider .count{ color: var(--muted-2); font-weight:400; }

/* legend chips */
.legend-row{ display:flex; gap:10px; flex-wrap:wrap; margin: 6px 0 4px; }
.legend-chip{ display:flex; align-items:center; gap:7px; font-family: var(--font-mono); font-size:11px; color: var(--muted); border:1px solid var(--rule-soft); padding:5px 10px; border-radius:20px; }
.dot{ width:8px; height:8px; border-radius:50%; display:inline-block; }
.dot-core{ background: var(--gold); } .dot-pe{ background: var(--teal); } .dot-oe{ background: var(--coral); }

/* ---------- buttons as glass course cards ---------- */
div[data-testid="stButton"] button{
  width: 100%;
  text-align: left;
  white-space: pre-line;
  background: var(--glass-bg) !important;
  backdrop-filter: blur(16px) saturate(150%);
  border: 1px solid var(--glass-border) !important;
  border-radius: 14px !important;
  color: var(--ink) !important;
  padding: 14px 16px !important;
  line-height: 1.5;
  transition: transform .15s ease, background .15s ease, border-color .15s ease;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
}
div[data-testid="stButton"] button:hover{
  transform: translateY(-2px);
  background: var(--glass-bg-strong) !important;
  border-color: rgba(255,255,255,0.32) !important;
}
div[data-testid="stButton"] button p{ font-size: 13.5px !important; }

/* category-tinted left edge via container key (Streamlit st.container(key=...)) */
div[class*="st-key-card_core_"] div[data-testid="stButton"] button{ border-left: 3px solid var(--gold) !important; }
div[class*="st-key-card_pe_"]   div[data-testid="stButton"] button{ border-left: 3px solid var(--teal) !important; }
div[class*="st-key-card_oe_"]   div[data-testid="stButton"] button{ border-left: 3px solid var(--coral) !important; }

/* sidebar + generic buttons (AI tabs) keep a calmer style */
section[data-testid="stSidebar"] div[data-testid="stButton"] button{ border-left: none !important; }

/* tabs */
button[data-baseweb="tab"]{ font-family: var(--font-mono) !important; font-size: 12.5px !important; }
div[data-testid="stTabs"] [data-baseweb="tab-list"]{
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  border: 1px solid var(--rule-soft);
  padding: 4px;
}

/* chat */
[data-testid="stChatMessage"]{
  background: var(--glass-bg) !important;
  backdrop-filter: blur(14px);
  border: 1px solid var(--glass-border);
  border-radius: 14px;
}
[data-testid="stChatInput"] textarea{ background: var(--glass-bg) !important; }

/* misc form widgets */
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input, .stSelectbox div[data-baseweb="select"]{
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 10px !important;
  color: var(--ink) !important;
}
[data-testid="stExpander"]{
  background: var(--glass-bg) !important;
  border: 1px solid var(--glass-border) !important;
  border-radius: 14px !important;
}

footer{ font-family: var(--font-mono); font-size: 11px; color: var(--muted-2); }
hr{ border-color: var(--rule-soft) !important; }
::selection{ background: var(--gold-soft); color: var(--ink); }
</style>

<div class="wallpaper-orbs">
  <div class="orb orb-gold"></div>
  <div class="orb orb-teal"></div>
  <div class="orb orb-coral"></div>
</div>
"""


def inject(st):
    st.markdown(CSS, unsafe_allow_html=True)
