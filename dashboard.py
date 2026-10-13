"""Panel ucznia i program ścieżki (HTML osadzany przez components.html).

Iframe nie dziedziczy motywu Streamlita, więc wykrywa go sam (po kolorze tła
aplikacji, a awaryjnie po ustawieniu systemu) i przełącza paletę jasną/ciemną.
Każda paleta ma jawnie dobrane kolory tekstu i tła, więc kontrast jest zawsze OK.
"""
import html
import math

import knowledge as kb

FONT = "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');"

THEME_VARS = """
:root{--surface:#ffffff;--surface2:#f9fafb;--line:#e4e7ec;--ink:#101828;--text:#344054;--muted:#667085;
  --track:#eaecf0;--accent:#2f5bea;--accent-text:#2f5bea;--accent-soft:#eaf0ff;--accent-strong:#1e40af;
  --ok-bg:#ecfdf3;--ok-line:#abefc6;--ok-pill-bg:#dcfae6;--ok-pill-fg:#067647;
  --warn-bg:#fffaeb;--warn-line:#fedf89;--warn-pill-bg:#fef0c7;--warn-pill-fg:#93370d;
  --bad-pill-bg:#fee4e2;--bad-pill-fg:#b42318}
html[data-theme="dark"]{--surface:#161b22;--surface2:#1b212b;--line:#2a3140;--ink:#f2f4f7;--text:#cbd2de;
  --muted:#98a2b3;--track:#2a3140;--accent:#3d68f0;--accent-text:#9db4ff;--accent-soft:rgba(61,104,240,.20);
  --accent-strong:#c3d1ff;
  --ok-bg:rgba(50,213,131,.10);--ok-line:rgba(50,213,131,.38);--ok-pill-bg:rgba(50,213,131,.16);--ok-pill-fg:#75e0a7;
  --warn-bg:rgba(253,176,34,.10);--warn-line:rgba(253,176,34,.38);--warn-pill-bg:rgba(253,176,34,.16);--warn-pill-fg:#fec84b;
  --bad-pill-bg:rgba(240,68,56,.18);--bad-pill-fg:#fda29b}
"""

# wykrycie motywu: tło aplikacji Streamlita (rodzic), a gdy to się nie uda, ustawienie systemu
THEME_JS = (
    "<script>(function(){function lum(c){var m=(c||'').match(/[\\d.]+/g);if(!m||m.length<3)return 1;"
    "var a=m.slice(0,3).map(function(v){v=v/255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});"
    "return .2126*a[0]+.7152*a[1]+.0722*a[2];}"
    "var dark=!!(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches);"
    "try{var el=window.parent.document.querySelector('.stApp');"
    "if(el){dark=lum(window.parent.getComputedStyle(el).backgroundColor)<0.4;}}catch(e){}"
    "document.documentElement.setAttribute('data-theme',dark?'dark':'light');})();</script>"
)

CSS = FONT + THEME_VARS + """
*{box-sizing:border-box}
body{margin:0;padding:4px 2px 12px;font-family:'Inter','Segoe UI',system-ui,-apple-system,Roboto,sans-serif;
  background:transparent;color:var(--text)}
.grid{display:grid;gap:16px;margin-bottom:16px}
.top{grid-template-columns:auto 1fr}
.kpis{grid-template-columns:repeat(auto-fit,minmax(170px,1fr))}
.two{grid-template-columns:repeat(auto-fit,minmax(330px,1fr))}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.card h3{margin:0 0 14px;font-size:15px;font-weight:600;color:var(--ink)}
.muted{color:var(--muted);font-size:13px}
.kpi .v{font-size:26px;font-weight:700;margin:6px 0 2px;line-height:1.15;letter-spacing:-.02em;color:var(--ink)}
.kpi .l{font-size:11.5px;color:var(--muted);text-transform:uppercase;letter-spacing:.06em;font-weight:600}
.kpi .s{font-size:12px;color:var(--muted)}
.ringbox{display:flex;align-items:center;gap:18px}
.ring{--p:0;width:104px;height:104px;border-radius:50%;flex:none;position:relative;
  background:conic-gradient(var(--accent) calc(var(--p)*1%),var(--track) 0);display:grid;place-items:center}
.ring::before{content:"";position:absolute;inset:11px;background:var(--surface);border-radius:50%}
.ring span{position:relative;font-weight:700;font-size:22px;color:var(--ink)}
.row{margin-bottom:13px}
.row .h{display:flex;justify-content:space-between;font-size:13px;margin-bottom:5px;color:var(--text)}
.bar{height:8px;border-radius:99px;background:var(--track);overflow:hidden}
.bar.thin{height:5px}
.bar i{display:block;height:100%;border-radius:99px;background:var(--accent)}
.radar{display:block;margin:0 auto;max-width:480px;width:100%;height:auto}
.rg{fill:none;stroke:var(--line)}
.rax{stroke:var(--line)}
.rpoly{fill:var(--accent);fill-opacity:.18;stroke:var(--accent);stroke-width:2}
.rdot{fill:var(--accent)}
.rt{fill:var(--text);font-size:11.5px}
.rv{fill:var(--accent-text);font-size:11px;font-weight:700}
.blk{margin-bottom:22px}
.blk:last-of-type{margin-bottom:6px}
.bh{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
.bn{font-size:13px;font-weight:700;color:var(--ink)}
.blk .bar{margin-bottom:12px}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:10px}
.tile{border:1px solid var(--line);border-radius:10px;padding:10px 12px;background:var(--surface2);min-height:68px}
.tile.m{background:var(--ok-bg);border-color:var(--ok-line)}
.tile.p{background:var(--warn-bg);border-color:var(--warn-line)}
.tile.next{outline:2px solid var(--accent);outline-offset:1px}
.tile .t{font-size:13px;font-weight:600;line-height:1.3;color:var(--ink)}
.tile .s{font-size:11.5px;color:var(--muted);margin-top:5px}
.badge{display:inline-block;background:var(--accent);color:#fff;border-radius:99px;
  font-size:10.5px;padding:1px 8px;margin-left:6px;vertical-align:1px}
.ev{display:flex;gap:12px;padding:10px 0;border-top:1px solid var(--line)}
.ev:first-of-type{border-top:0}
.pill{flex:none;min-width:52px;text-align:center;border-radius:8px;padding:4px 6px;font-size:12px;font-weight:700}
.pill.hi{background:var(--ok-pill-bg);color:var(--ok-pill-fg)}
.pill.mid{background:var(--warn-pill-bg);color:var(--warn-pill-fg)}
.pill.lo{background:var(--bad-pill-bg);color:var(--bad-pill-fg)}
.ev .t{font-size:13.5px;font-weight:600;color:var(--ink)}
.ev .e{font-size:12.5px;color:var(--muted);margin-top:2px}
.legend{display:flex;gap:14px;margin-top:6px;font-size:12px;color:var(--muted);flex-wrap:wrap}
.dot{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:5px;vertical-align:-1px;
  border:1px solid var(--line)}
"""

OUTLINE_CSS = FONT + THEME_VARS + """
*{box-sizing:border-box}
body{margin:0;padding:2px;font-family:'Inter','Segoe UI',system-ui,-apple-system,Roboto,sans-serif;
  background:transparent;color:var(--text)}
.wrap{background:var(--surface);border:1px solid var(--line);border-radius:12px;overflow:hidden}
.ohead{padding:14px 16px;border-bottom:1px solid var(--line)}
.ohead .t{font-weight:600;font-size:14px;color:var(--ink)}
.ohead .s{font-size:12px;color:var(--muted);margin-top:2px}
.ob{padding:6px 8px 8px}
.obh{display:flex;justify-content:space-between;padding:12px 10px 6px;font-size:11px;font-weight:700;
  letter-spacing:.06em;color:var(--muted);text-transform:uppercase}
.it{display:flex;gap:10px;align-items:center;padding:8px 10px;border-radius:8px;font-size:13px;line-height:1.3;
  color:var(--text)}
.it .ic{flex:none;width:18px;height:18px;border-radius:50%;display:grid;place-items:center;
  font-size:10px;font-weight:700;color:#fff}
.it.m .ic{background:#12b76a}
.it.p .ic{background:#f79009}
.it.n .ic{border:2px solid var(--track)}
.it.cur{background:var(--accent-soft);font-weight:600;color:var(--accent-strong)}
.it.cur .ic{border:2px solid var(--accent);background:transparent;color:var(--accent-text)}
.it .lv{margin-left:auto;font-size:11px;color:var(--muted);font-weight:500}
.it.cur .lv{color:var(--accent-strong)}
"""

# iframe sam dopasowuje wysokość do treści (wyliczona wysokość to tylko zapas)
AUTOSIZE = (
    "<script>(function(){function f(){try{var h=document.documentElement.scrollHeight;"
    "if(window.frameElement){window.frameElement.style.height=h+'px';}}catch(e){}}"
    "f();if(window.ResizeObserver){new ResizeObserver(f).observe(document.body);}"
    "window.addEventListener('load',f);})();</script>"
)

MODE_LABEL = {"placement": "Diagnoza wiedzy", "teach": "Następny temat", "done": "Ukończone"}


def esc(x):
    return html.escape(str(x))


def _radar_svg(cats):
    n = len(cats)
    cx, cy, radius = 180, 150, 92

    def pt(i, frac):
        a = -math.pi / 2 + 2 * math.pi * i / n
        return cx + radius * frac * math.cos(a), cy + radius * frac * math.sin(a)

    rings = ""
    for frac in (0.25, 0.5, 0.75, 1.0):
        pts = " ".join("%.1f,%.1f" % pt(i, frac) for i in range(n))
        rings += '<polygon class="rg" points="%s"/>' % pts
    axes = "".join(
        '<line class="rax" x1="%d" y1="%d" x2="%.1f" y2="%.1f"/>' % ((cx, cy) + pt(i, 1))
        for i in range(n)
    )
    data = " ".join("%.1f,%.1f" % pt(i, max(c["avg"], 3) / 100) for i, c in enumerate(cats))
    dots = "".join(
        '<circle class="rdot" cx="%.1f" cy="%.1f" r="3.5"/>' % pt(i, max(c["avg"], 3) / 100)
        for i, c in enumerate(cats)
    )
    labels = ""
    for i, c in enumerate(cats):
        x, y = pt(i, 1.2)
        anchor = "middle"
        if x > cx + 14:
            anchor = "start"
        elif x < cx - 14:
            anchor = "end"
        name = c["category"] if len(c["category"]) <= 20 else c["category"][:19] + "…"
        labels += (
            '<text class="rt" x="%.1f" y="%.1f" text-anchor="%s">%s</text>'
            '<text class="rv" x="%.1f" y="%.1f" text-anchor="%s">%d%%</text>'
            % (x, y, anchor, esc(name), x, y + 13, anchor, c["avg"])
        )
    return (
        '<svg class="radar" viewBox="-70 0 500 310" xmlns="http://www.w3.org/2000/svg">'
        + rings + axes + '<polygon class="rpoly" points="%s"/>' % data + dots + labels + "</svg>"
    )


def _is_mastered(t):
    return t["level"] is not None and t["level"] >= kb.MASTERED


def _groups(ts):
    groups = {}
    for t in ts:
        groups.setdefault(t["category"], []).append(t)
    return groups


def _tile(t, next_id):
    lvl = t["level"]
    if _is_mastered(t):
        cls = "m"
        status = "✓ Opanowany" + (" (wywnioskowany)" if t["inferred"] else "")
    elif lvl is not None:
        cls = "p"
        status = "W trakcie: %d%%" % lvl
    else:
        cls = "n"
        status = "Do poznania"
    if t["id"] == next_id:
        cls += " next"
    badge = '<span class="badge">teraz</span>' if t["id"] == next_id else ""
    return '<div class="tile %s"><div class="t">%s%s</div><div class="s">%s</div></div>' % (
        cls, esc(t["title"]), badge, status)


def _blocks_html(ts, next_id):
    out = ""
    for cat, items in _groups(ts).items():
        m = sum(1 for t in items if _is_mastered(t))
        pct = round(100 * m / len(items))
        out += (
            '<div class="blk"><div class="bh"><span class="bn">%s</span>'
            '<span class="muted">%d / %d</span></div>'
            '<div class="bar thin"><i style="width:%d%%"></i></div>'
            '<div class="tiles">%s</div></div>'
        ) % (esc(cat), m, len(items), pct, "".join(_tile(t, next_id) for t in items))
    return out


def build_dashboard(path=None):
    """Zwraca (html, wysokość_w_px) panelu dla ścieżki nauki."""
    path = path or kb.active_path()
    stats = kb.path_stats(path)
    cats = kb.category_stats(path)
    ts = kb.get_topics(path)
    rec = kb.recommend(path)
    events = kb.recent_events(path, 6)
    next_id = rec["topic"]["id"] if rec["topic"] else None
    next_title = rec["topic"]["title"] if rec["topic"] else "Wszystko opanowane"
    courses = len(kb.list_courses())

    sub_m = ("w tym wywnioskowane: %d" % stats["inferred"]) if stats["inferred"] else "potwierdzone zadaniami"
    kpi_label = "Nowy blok: od podstaw" if rec.get("block_start") else MODE_LABEL[rec["mode"]]

    top = (
        '<div class="grid top">'
        '<div class="card"><div class="ringbox">'
        '<div class="ring" style="--p:%d"><span>%d%%</span></div>'
        '<div><h3 style="margin-bottom:4px">Postęp ścieżki</h3>'
        '<div class="muted">%s</div></div></div></div>'
        '<div class="grid kpis" style="margin:0">'
        '<div class="card kpi"><div class="l">Opanowane tematy</div>'
        '<div class="v">%d / %d</div><div class="s">%s</div></div>'
        '<div class="card kpi"><div class="l">W trakcie</div>'
        '<div class="v">%d</div><div class="s">tematy, nad którymi pracujesz</div></div>'
        '<div class="card kpi"><div class="l">%s</div>'
        '<div class="v" style="font-size:16px;margin-top:10px">%s</div></div>'
        '<div class="card kpi"><div class="l">Dodane kursy</div>'
        '<div class="v">%d</div><div class="s">poza ścieżką podstawową</div></div>'
        "</div></div>"
    ) % (
        stats["percent"], stats["percent"], esc(path),
        stats["mastered"], stats["total"], sub_m,
        stats["started"],
        kpi_label, esc(next_title),
        courses,
    )

    bars = "".join(
        '<div class="row"><div class="h"><span>%s</span><span class="muted">%d/%d tematów</span></div>'
        '<div class="bar"><i style="width:%d%%"></i></div></div>'
        % (esc(c["category"]), c["mastered"], c["total"], c["avg"])
        for c in cats
    )
    bars_card = '<div class="card"><h3>Opanowanie według bloków</h3>%s</div>' % bars

    if len(cats) >= 3:
        radar_card = '<div class="card"><h3>Mapa umiejętności</h3>%s</div>' % _radar_svg(cats)
        charts = '<div class="grid two">%s%s</div>' % (radar_card, bars_card)
        charts_h = 290
    else:
        charts = '<div class="grid">%s</div>' % bars_card
        charts_h = 70 + 40 * len(cats)

    groups = _groups(ts)
    program = (
        '<div class="card"><h3>Program ścieżki</h3>%s'
        '<div class="legend"><span><i class="dot" style="background:var(--ok-line)"></i>opanowany</span>'
        '<span><i class="dot" style="background:var(--warn-line)"></i>w trakcie</span>'
        '<span><i class="dot" style="background:var(--surface2)"></i>do poznania</span></div></div>'
    ) % _blocks_html(ts, next_id)
    program_h = 70 + sum(58 + 58 * math.ceil(len(g) / 3) for g in groups.values())

    if events:
        rows = ""
        for e in events:
            cls = "hi" if e["level"] >= kb.MASTERED else ("mid" if e["level"] >= 50 else "lo")
            rows += (
                '<div class="ev"><div class="pill %s">%d%%</div><div>'
                '<div class="t">%s</div><div class="e">%s · %s</div></div></div>'
            ) % (cls, e["level"], esc(e["title"]), esc(e["evidence"] or "bez komentarza"), esc(e["ts"]))
        activity = '<div class="card"><h3>Ostatnie oceny nauczyciela</h3>%s</div>' % rows
        act_h = 70 + 58 * len(events)
    else:
        activity = ('<div class="card"><h3>Ostatnie oceny nauczyciela</h3>'
                    '<div class="muted">Jeszcze brak ocen. Zacznij rozmowę z nauczycielem, '
                    'a ocena pojawi się tutaj wraz z uzasadnieniem.</div></div>')
        act_h = 130

    doc = ("<!doctype html><html><head><meta charset='utf-8'>%s<style>%s</style></head>"
           "<body>%s%s%s%s%s</body></html>") % (THEME_JS, CSS, top, charts, program, activity, AUTOSIZE)
    height = 130 + charts_h + program_h + act_h + 200
    return doc, height


def build_outline(path=None):
    """Program ścieżki jako lista (jak spis lekcji w kursie): HTML do iframe."""
    path = path or kb.active_path()
    ts = kb.get_topics(path)
    stats = kb.path_stats(path)
    rec = kb.recommend(path)
    cur_id = rec["topic"]["id"] if rec["topic"] else None

    body = ""
    for cat, items in _groups(ts).items():
        m = sum(1 for t in items if _is_mastered(t))
        rows = ""
        for t in items:
            if t["id"] == cur_id:
                cls, icon, right = "cur", "▶", "teraz"
            elif _is_mastered(t):
                cls, icon, right = "m", "✓", ""
            elif t["level"] is not None:
                cls, icon, right = "p", "·", "%d%%" % t["level"]
            else:
                cls, icon, right = "n", "", ""
            rows += '<div class="it %s"><span class="ic">%s</span><span>%s</span><span class="lv">%s</span></div>' % (
                cls, icon, esc(t["title"]), right)
        body += '<div class="obh"><span>%s</span><span>%d/%d</span></div>%s' % (esc(cat), m, len(items), rows)

    head = ('<div class="ohead"><div class="t">Program ścieżki</div>'
            '<div class="s">%s · %d / %d opanowanych</div></div>') % (
        esc(path), stats["mastered"], stats["total"])
    script = ("<script>var c=document.querySelector('.cur');"
              "if(c){window.scrollTo(0,Math.max(0,c.offsetTop-160));}</script>")
    return ("<!doctype html><html><head><meta charset='utf-8'>%s<style>%s</style></head>"
            "<body><div class='wrap'>%s<div class='ob'>%s</div></div>%s</body></html>") % (
        THEME_JS, OUTLINE_CSS, head, body, script)
