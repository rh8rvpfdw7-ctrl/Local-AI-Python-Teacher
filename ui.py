"""Wspólny wygląd aplikacji: CSS oraz fragmenty HTML.

Zasada kontrastu: elementy Streamlita zostają w jego motywie (jasnym lub
ciemnym), a nasze karty NIE ustawiają własnego koloru tekstu. Tekst jest
dziedziczony z motywu, a tła i ramki są półprzezroczyste (neutralna szarość),
więc tekst i tło zawsze mają kontrast, niezależnie od motywu.
Funkcje *_html nie wymagają Streamlita, więc można je testować osobno.
"""
import html

import knowledge as kb

ACC = "#3d68f0"
# kolor akcentu jako tekst: mieszany z kolorem tekstu motywu (jaśniejszy w ciemnym, ciemniejszy w jasnym)
ACC_TXT = "color:%s;color:color-mix(in srgb,%s 62%%,currentColor)" % (ACC, ACC)
GREEN_TXT = "color:#067647;color:color-mix(in srgb,#12b76a 38%,currentColor)"
AMBER_TXT = "color:#93370d;color:color-mix(in srgb,#f79009 38%,currentColor)"

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root{--accent:@ACC@;--accent-hover:#2f5bea;--line:rgba(127,127,127,.30);--card:rgba(127,127,127,.07);
  --hover:rgba(127,127,127,.15);--track:rgba(127,127,127,.28)}

/* ---- baza: kolory tekstu i tła zostają w motywie Streamlita ---- */
.stApp,.stApp p,.stApp li,.stApp label,.stApp button,.stApp input,.stApp textarea,
.stApp h1,.stApp h2,.stApp h3{font-family:'Inter','Segoe UI',system-ui,-apple-system,sans-serif}
#MainMenu,footer,.stDeployButton,[data-testid="stDecoration"],[data-testid="stToolbar"]{visibility:hidden}
header[data-testid="stHeader"]{background:transparent}
.block-container{padding-top:1.2rem;padding-bottom:7rem;max-width:1320px}
.m{opacity:.76}

/* ---- pasek boczny ---- */
section[data-testid="stSidebar"]{border-right:1px solid var(--line)}
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"]{gap:.3rem}
section[data-testid="stSidebar"] .stButton > button{width:100%;justify-content:flex-start;gap:.6rem;
  border:0;background:transparent;color:inherit;font-weight:500;font-size:14px;
  padding:.55rem .75rem;border-radius:8px;box-shadow:none}
section[data-testid="stSidebar"] .stButton > button > div{justify-content:flex-start}
section[data-testid="stSidebar"] .stButton > button:hover{background:var(--hover);color:inherit}
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]{
  background:rgba(61,104,240,.16);@ACCTXT@;font-weight:600;border:0;
  box-shadow:inset 3px 0 0 var(--accent)}
section[data-testid="stSidebar"] button[kind="primary"] p,
section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p{color:inherit}
section[data-testid="stSidebar"] [data-baseweb="select"] > div{border-radius:8px}
.brand{display:flex;align-items:center;gap:10px;padding:2px 4px 14px}
.brand .mark{width:32px;height:32px;border-radius:8px;background:var(--accent);display:grid;place-items:center;flex:none}
.brand .mark svg{width:18px;height:18px}
.brand .bt{font-weight:700;font-size:15px;line-height:1.2}
.brand .bs{font-size:12px;opacity:.74}
.side-label{font-size:11px;letter-spacing:.07em;text-transform:uppercase;font-weight:600;
  margin:18px 4px 4px;opacity:.74}
.side-card{border:1px solid var(--line);background:var(--card);border-radius:10px;padding:12px 14px;margin-top:8px}
.side-card .st{font-size:13px;font-weight:600;line-height:1.35}
.side-card .srow{display:flex;justify-content:space-between;font-size:12px;margin:8px 0 6px}
.side-card .snext{font-size:12px;margin-top:10px;padding-top:10px;border-top:1px solid var(--line)}
.side-card .snext b{font-weight:600}
.side-foot{display:flex;align-items:center;gap:8px;margin:22px 4px 0;font-size:12px}
.side-foot .dot{width:7px;height:7px;border-radius:50%;background:#12b76a}

/* ---- elementy wspólne ---- */
.bar{height:6px;border-radius:99px;background:var(--track);overflow:hidden}
.bar i{display:block;height:100%;border-radius:99px;background:var(--accent)}
.sect{font-size:15px;font-weight:600;margin:24px 0 12px}
.topbar{display:flex;justify-content:space-between;align-items:center;margin:0 0 18px}
.crumb{font-size:13.5px;display:flex;gap:8px;align-items:center}
.crumb .m{opacity:.76}
.crumb b{font-weight:600}
.chip{border:1px solid var(--line);background:var(--card);border-radius:8px;padding:5px 12px;font-size:12.5px}
.pill{display:inline-block;border-radius:6px;padding:2px 9px;font-size:11.5px;font-weight:600}
.pill.diag{background:rgba(247,144,9,.18);@AMBERTXT@}
.pill.new{background:rgba(61,104,240,.16);@ACCTXT@}
.pill.teach,.pill.done{background:rgba(18,183,106,.16);@GREENTXT@}
.hero{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);
  border-radius:12px;padding:18px 22px}
.hero .eyebrow{display:flex;gap:10px;align-items:center;font-size:11.5px;letter-spacing:.07em;font-weight:600}
.hero .eyebrow .k{@ACCTXT@}
.hero .h{font-size:22px;font-weight:700;margin:8px 0 2px;letter-spacing:-.01em}
.hero .sub{font-size:13.5px;margin-bottom:12px;opacity:.78}
.hero .hnote{font-size:12px;margin-top:7px;opacity:.76}
.lhead{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 20px;margin-bottom:14px}
.lhead .l1{display:flex;gap:10px;align-items:center;font-size:13px}
.lhead .l1 .where{opacity:.78}
.lhead .l2{font-size:19px;font-weight:700;margin:8px 0 10px;letter-spacing:-.01em}
.lhead .l3{font-size:12.5px;margin-top:7px;opacity:.76}
.ccard{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin-bottom:10px}
.ccard.act{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.chead{display:flex;justify-content:space-between;align-items:center;margin-bottom:14px}
.cico{width:40px;height:40px;border-radius:10px;background:rgba(61,104,240,.16);display:grid;place-items:center;@ACCTXT@}
.cico.udemy{background:rgba(124,58,237,.16);color:#7c3aed;color:color-mix(in srgb,#7c3aed 55%,currentColor)}
.cico svg{width:20px;height:20px}
.ctag{background:var(--hover);border-radius:6px;font-size:11.5px;padding:3px 9px;font-weight:600}
.ctitle{font-weight:600;font-size:15px;line-height:1.35;min-height:40px}
.cmeta{font-size:12.5px;margin:2px 0 12px;opacity:.76}
.crow{display:flex;justify-content:space-between;font-size:12.5px;margin-top:8px}
.crow .m{opacity:.76}

/* ---- widgety Streamlita (obszar główny): tylko kształt i akcent ---- */
.stButton > button,button[data-testid="stBaseButton-secondary"],button[data-testid="stBaseButton-primary"]{
  border-radius:8px;font-weight:600;font-size:14px;padding:.5rem 1rem;transition:background .12s,border-color .12s}
.stButton > button[kind="secondary"]:hover,button[data-testid="stBaseButton-secondary"]:hover{
  border-color:var(--accent);@ACCTXT@}
.stButton > button[kind="primary"],button[data-testid="stBaseButton-primary"]{
  background:var(--accent);border:1px solid var(--accent);color:#fff}
.stButton > button[kind="primary"] p,button[data-testid="stBaseButton-primary"] p{color:#fff}
.stButton > button[kind="primary"]:hover,button[data-testid="stBaseButton-primary"]:hover{
  background:var(--accent-hover);border-color:var(--accent-hover);color:#fff}
.stTextArea textarea,.stTextInput input{border-radius:8px}
[data-baseweb="select"] > div{border-radius:8px}
[data-testid="stExpander"]{border:1px solid var(--line);border-radius:12px}
[data-testid="stExpander"] summary{font-weight:600}
[data-testid="stChatMessage"]{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]){background:rgba(61,104,240,.10)}
[data-testid="stChatInput"]{border-radius:10px}
"""
CSS = (CSS.replace("@ACC@", ACC).replace("@ACCTXT@", ACC_TXT)
       .replace("@GREENTXT@", GREEN_TXT).replace("@AMBERTXT@", AMBER_TXT))


def esc(x):
    return html.escape(str(x))


def apply_theme():
    import streamlit as st
    st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)


# ---------- ikony (SVG liniowe, kolor z currentColor) ----------
def _svg(inner, color="currentColor"):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" '
            'stroke-linejoin="round">%s</svg>') % (color, inner)


ICON_CODE = '<polyline points="8 6 3 12 8 18"/><polyline points="16 6 21 12 16 18"/>'
ICON_CAP = '<path d="M22 10L12 5 2 10l10 5 10-5z"/><path d="M6 12v5c3 2 9 2 12 0v-5"/>'


# ---------- fragmenty HTML ----------
def brand_html():
    return ('<div class="brand"><div class="mark">%s</div><div>'
            '<div class="bt">Python Tutor</div><div class="bs">Nauka z nauczycielem AI</div></div></div>'
            % _svg(ICON_CODE, "#fff"))


def sidebar_course_html(path, stats, rec):
    nxt = ""
    if rec["topic"]:
        nxt = '<div class="snext"><span class="m">Następny temat</span><br><b>%s</b></div>' % esc(rec["topic"]["title"])
    return (
        '<div class="side-card"><div class="st">%s</div>'
        '<div class="srow"><span class="m">%d / %d tematów</span><b>%d%%</b></div>'
        '<div class="bar"><i style="width:%d%%"></i></div>%s</div>'
    ) % (esc(path), stats["mastered"], stats["total"], stats["percent"], stats["percent"], nxt)


def sidebar_footer_html(model):
    return '<div class="side-foot"><span class="dot"></span><span class="m">Model: %s</span></div>' % esc(model)


def topbar_html(page_title, path, stats):
    return (
        '<div class="topbar"><div class="crumb"><span class="m">Python Tutor</span><span class="m">/</span>'
        '<b>%s</b></div><div class="chip">%s · %d%%</div></div>'
    ) % (esc(page_title), esc(path), stats["percent"])


def _mode_label(rec):
    if rec["mode"] == "placement":
        return "Diagnoza wiedzy", "diag"
    if rec["mode"] == "done":
        return "Ścieżka ukończona", "done"
    if rec.get("block_start"):
        return "Nowy blok · od podstaw", "new"
    return "W trakcie nauki", "teach"


def hero_html(rec, stats):
    label, kind = _mode_label(rec)
    if rec["mode"] == "done":
        title = "Opanowałeś cały materiał tej ścieżki"
        sub = "Możesz wrócić do dowolnego tematu albo dodać nowy kurs"
    else:
        title = rec["topic"]["title"]
        sub = rec["topic"]["category"]
    return (
        '<div class="hero"><div class="eyebrow"><span class="k">KONTYNUUJ NAUKĘ</span>'
        '<span class="pill %s">%s</span></div><div class="h">%s</div>'
        '<div class="sub">%s</div><div class="bar"><i style="width:%d%%"></i></div>'
        '<div class="hnote">%d z %d tematów opanowanych</div></div>'
    ) % (kind, esc(label), esc(title), esc(sub), stats["percent"], stats["mastered"], stats["total"])


def lesson_head_html(path=None):
    """Nagłówek widoku nauczyciela: bieżący temat i postęp bloku."""
    path = path or kb.active_path()
    rec = kb.recommend(path)
    label, kind = _mode_label(rec)
    if rec["mode"] == "done":
        return ('<div class="lhead"><div class="l1"><span class="pill done">%s</span></div>'
                '<div class="l2">Wszystkie tematy tej ścieżki są opanowane</div></div>') % esc(label)
    t = rec["topic"]
    ts = kb.get_topics(path)
    multi = len({x["category"] for x in ts}) > 1
    block = [x for x in ts if x["category"] == t["category"]] if multi else ts
    done = sum(1 for x in block if x["level"] is not None and x["level"] >= kb.MASTERED)
    pct = round(100 * done / len(block)) if block else 0
    where = t["category"] if multi else "Cała ścieżka"
    return (
        '<div class="lhead"><div class="l1"><span class="pill %s">%s</span><span class="where">%s</span></div>'
        '<div class="l2">%s</div><div class="bar"><i style="width:%d%%"></i></div>'
        '<div class="l3">Postęp bloku: %d / %d tematów opanowanych</div></div>'
    ) % (kind, esc(label), esc(where), esc(t["title"]), pct, done, len(block))


def course_card_html(path, active, is_course):
    stats = kb.path_stats(path)
    ts = kb.get_topics(path)
    blocks = len({t["category"] for t in ts})
    if is_course:
        title = path.split(": ", 1)[-1]
        meta = "%d sekcji" % stats["total"]
        head = '<div class="chead"><div class="cico udemy">%s</div><span class="ctag">Udemy</span></div>' % _svg(ICON_CAP)
    else:
        title = path
        meta = "%d tematów · %d bloków" % (stats["total"], blocks)
        head = '<div class="chead"><div class="cico">%s</div><span class="ctag">Ścieżka podstawowa</span></div>' % _svg(ICON_CODE)
    return (
        '<div class="ccard%s">%s<div class="ctitle">%s</div><div class="cmeta">%s</div>'
        '<div class="bar"><i style="width:%d%%"></i></div>'
        '<div class="crow"><span class="m">%d / %d opanowanych</span><b>%d%%</b></div></div>'
    ) % (" act" if active else "", head, esc(title), esc(meta),
         stats["percent"], stats["mastered"], stats["total"], stats["percent"])
