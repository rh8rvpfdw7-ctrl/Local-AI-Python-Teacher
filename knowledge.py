"""Model wiedzy ucznia (SQLite, plik tutor.db).

Ścieżka nauki = uporządkowana lista tematów. Kolejność oznacza też zależności:
temat ma sens po opanowaniu poprzednich. Poziom opanowania (0-100) zapisuje
agent na podstawie tego, co uczeń faktycznie zrobił, a nie jego deklaracji.
"""
import re
import sqlite3
from contextlib import closing
from datetime import datetime

DB_FILE = "tutor.db"
MASTERED = 80          # od tego poziomu temat jest opanowany
CORE_PATH = "Python od zera"

# (kategoria, [(temat, zakres), ...]) - kolejność = ścieżka nauki
CORE_TOPICS = [
    ("Podstawy", [
        ("Zmienne i typy podstawowe", "int, float, str, bool, przypisanie, type()"),
        ("Napisy (string) i ich metody", "len, lower/upper/title, strip, split/join, f-stringi"),
        ("Indeksowanie i slicing", "indeksy dodatnie i ujemne, wycinki [a:b:c], odwracanie [::-1]"),
        ("Liczby i operatory", "+ - * / // % **, priorytety działań, operatory skrócone +="),
        ("Wartości logiczne i porównania", "True/False, ==, !=, <, >, and/or/not"),
        ("Konwersja typów, input() i print()", "int(), float(), str(), input(), print(sep, end)"),
    ]),
    ("Sterowanie przepływem", [
        ("Instrukcja if / elif / else", "warunki, wiele gałęzi, wcięcia"),
        ("Zagnieżdżone warunki", "warunki w warunkach, łączenie and/or, typowe pułapki"),
        ("Pętla for i range()", "iteracja po liście i napisie, range(start, stop, krok)"),
        ("Pętla while, break, continue", "warunek stopu, pętla nieskończona, else w pętli"),
        ("Obsługa wyjątków", "try/except/else/finally, ValueError, ZeroDivisionError"),
    ]),
    ("Struktury danych", [
        ("Listy", "tworzenie, append/insert/pop/remove, sort/sorted, len/min/max"),
        ("Krotki i rozpakowywanie", "niemutowalność, a, b = b, a, rozpakowywanie"),
        ("Słowniki", "klucze i wartości, get, items/keys/values, setdefault, iteracja"),
        ("Zbiory (set)", "unikalność, suma/część wspólna/różnica, operator in"),
        ("List comprehension", "[x for x in ... if ...], dict i set comprehension"),
        ("enumerate, zip i wiele sekwencji", "iteracja z indeksem, łączenie list, zagnieżdżone pętle"),
    ]),
    ("Funkcje", [
        ("Definiowanie funkcji i return", "def, parametry, wartość zwracana, None"),
        ("Parametry funkcji", "wartości domyślne, argumenty nazwane, *args, **kwargs"),
        ("Zakres zmiennych", "zmienne lokalne i globalne, global, efekty uboczne"),
        ("Sortowanie z kluczem i lambda", "sorted(key=...), lambda, map, filter"),
    ]),
    ("Moduły i pliki", [
        ("Importy i biblioteki standardowe", "import, from ... import, random, datetime, math"),
        ("Praca z plikami", "open, with, read/write, tryby r/w/a"),
        ("JSON", "json.load/dump, słowniki jako dane"),
    ]),
    ("Programowanie obiektowe", [
        ("Klasy i obiekty", "class, __init__, self, metody, atrybuty"),
        ("Enkapsulacja", "atrybuty prywatne _x/__x, @property"),
        ("Dziedziczenie", "class B(A), super(), nadpisywanie metod"),
        ("Polimorfizm i abstrakcja", "wspólny interfejs, klasy abstrakcyjne (abc)"),
    ]),
    ("Jakość kodu", [
        ("Debugowanie", "czytanie tracebacków, print-debugging, typowe błędy"),
        ("Testowanie z assert", "assert, przypadki brzegowe, proste testy funkcji"),
    ]),
]


# ---------- baza ----------
def _run(sql, params=(), fetch=False):
    with closing(sqlite3.connect(DB_FILE)) as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall() if fetch else None
        conn.commit()
        return rows


def _rows(sql, params=()):
    return _run(sql, params, fetch=True)


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def init_db():
    _run(
        "CREATE TABLE IF NOT EXISTS topics (id INTEGER PRIMARY KEY, "
        "path TEXT NOT NULL, category TEXT NOT NULL, title TEXT NOT NULL, "
        "details TEXT NOT NULL DEFAULT '', position INTEGER NOT NULL)"
    )
    _run(
        "CREATE TABLE IF NOT EXISTS mastery (topic_id INTEGER PRIMARY KEY, "
        "level INTEGER NOT NULL, inferred INTEGER NOT NULL DEFAULT 0, "
        "evidence TEXT NOT NULL DEFAULT '', updated TEXT NOT NULL)"
    )
    _run(
        "CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY, "
        "topic_id INTEGER NOT NULL, level INTEGER NOT NULL, "
        "evidence TEXT NOT NULL DEFAULT '', ts TEXT NOT NULL)"
    )
    _run(
        "CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, "
        "title TEXT NOT NULL, provider TEXT NOT NULL, "
        "url TEXT NOT NULL DEFAULT '', path TEXT NOT NULL UNIQUE, "
        "added TEXT NOT NULL)"
    )
    _run(
        "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, "
        "value TEXT NOT NULL)"
    )
    if not _rows("SELECT 1 FROM topics WHERE path = ? LIMIT 1", (CORE_PATH,)):
        pos = 0
        for category, items in CORE_TOPICS:
            for title, details in items:
                pos += 1
                _run(
                    "INSERT INTO topics (path, category, title, details, position) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (CORE_PATH, category, title, details, pos),
                )


def get_setting(key, default=None):
    rows = _rows("SELECT value FROM settings WHERE key = ?", (key,))
    return rows[0][0] if rows else default


def set_setting(key, value):
    _run("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))


# ---------- ścieżki i tematy ----------
def list_paths():
    rows = _rows("SELECT path FROM topics GROUP BY path ORDER BY MIN(id)")
    return [r[0] for r in rows]


def active_path():
    path = get_setting("active_path", CORE_PATH)
    return path if path in list_paths() else CORE_PATH


def get_topics(path=None):
    """Tematy ścieżki w kolejności nauki; level=None oznacza 'nieocenione'."""
    rows = _rows(
        "SELECT t.id, t.category, t.title, t.details, t.position, "
        "m.level, m.inferred, m.evidence "
        "FROM topics t LEFT JOIN mastery m ON m.topic_id = t.id "
        "WHERE t.path = ? ORDER BY t.position, t.id",
        (path or active_path(),),
    )
    keys = ("id", "category", "title", "details", "position",
            "level", "inferred", "evidence")
    return [dict(zip(keys, r)) for r in rows]


def set_mastery(topic_id, level, evidence=""):
    """Zapisuje ocenę tematu. Zwraca tytuł tematu.

    Tylko podczas diagnozy poziomu (zamówionej przez ucznia): jeśli temat jest
    opanowany, wcześniejsze nieocenione tematy zaliczamy jako 'wywnioskowane'.
    W zwykłej nauce nic nie jest zaliczane automatycznie.
    """
    rows = _rows("SELECT path, position, title FROM topics WHERE id = ?", (topic_id,))
    if not rows:
        raise ValueError(f"nie ma tematu o id {topic_id}")
    path, position, title = rows[0]
    level = max(0, min(100, int(level)))
    evidence = (evidence or "").strip()[:300]
    ts = _now()
    _run(
        "INSERT OR REPLACE INTO mastery (topic_id, level, inferred, evidence, updated) "
        "VALUES (?, ?, 0, ?, ?)",
        (topic_id, level, evidence, ts),
    )
    _run(
        "INSERT INTO events (topic_id, level, evidence, ts) VALUES (?, ?, ?, ?)",
        (topic_id, level, evidence, ts),
    )
    if level >= MASTERED and get_setting(f"diag:{path}") == "1":
        earlier = _rows(
            "SELECT t.id FROM topics t LEFT JOIN mastery m ON m.topic_id = t.id "
            "WHERE t.path = ? AND t.position < ? AND m.topic_id IS NULL",
            (path, position),
        )
        for (tid,) in earlier:
            _run(
                "INSERT INTO mastery (topic_id, level, inferred, evidence, updated) "
                "VALUES (?, ?, 1, ?, ?)",
                (tid, MASTERED, f"Wywnioskowane z opanowania tematu: {title}", ts),
            )
    return title


def recent_events(path=None, limit=6):
    rows = _rows(
        "SELECT t.title, e.level, e.evidence, e.ts FROM events e "
        "JOIN topics t ON t.id = e.topic_id WHERE t.path = ? "
        "ORDER BY e.id DESC LIMIT ?",
        (path or active_path(), limit),
    )
    return [dict(title=r[0], level=r[1], evidence=r[2], ts=r[3]) for r in rows]


# ---------- statystyki do panelu ----------
def path_stats(path=None):
    ts = get_topics(path)
    n = len(ts)
    mastered = sum(1 for t in ts if t["level"] is not None and t["level"] >= MASTERED)
    started = sum(1 for t in ts if t["level"] is not None and t["level"] < MASTERED)
    inferred = sum(1 for t in ts if t["inferred"])
    return {
        "total": n,
        "mastered": mastered,
        "started": started,
        "inferred": inferred,
        "percent": round(100 * mastered / n) if n else 0,
    }


def category_stats(path=None):
    cats = {}
    for t in get_topics(path):
        c = cats.setdefault(
            t["category"],
            {"category": t["category"], "total": 0, "mastered": 0, "sum": 0},
        )
        lvl = t["level"] or 0
        c["total"] += 1
        c["sum"] += lvl
        if lvl >= MASTERED:
            c["mastered"] += 1
    out = []
    for c in cats.values():
        c["avg"] = round(c["sum"] / c["total"])
        out.append(c)
    return out


# ---------- silnik nauczyciela ----------
def _teach(ts, i):
    """Wynik 'nauka' dla tematu ts[i], z informacją o początku bloku.

    Blokiem jest kategoria (np. 'Struktury danych'). W ścieżce z jedną
    kategorią (np. kurs z Udemy) blokiem jest każdy temat (sekcja).
    Początek bloku = uczeń nie wykazał jeszcze w nim własnej wiedzy
    (liczą się tylko oceny bezpośrednie >= 50, nie wywnioskowane).
    """
    topic = ts[i]
    multi = len({t["category"] for t in ts}) > 1
    members = [t for t in ts if t["category"] == topic["category"]] if multi else [topic]
    started = any(
        t["level"] is not None and t["level"] >= 50 and not t["inferred"]
        for t in members
    )
    return {
        "mode": "teach",
        "topic": topic,
        "total": len(ts),
        "block": topic["category"] if multi else topic["title"],
        "block_start": not started,
    }


def _mastered(t):
    return t["level"] is not None and t["level"] >= MASTERED


def _event_max():
    return _rows("SELECT COALESCE(MAX(id), 0) FROM events")[0][0]


def set_pointer(path, topic_id):
    """Uczeń wybrał temat: od niego nauka toczy się po kolei."""
    set_setting(f"ptr:{path}", f"{int(topic_id)}:{_event_max()}")


def get_pointer(path):
    value = get_setting(f"ptr:{path}")
    if not value:
        return None
    try:
        tid, base = value.split(":")
        return int(tid), int(base)
    except ValueError:
        return None


def clear_pointer(path):
    _run("DELETE FROM settings WHERE key = ?", (f"ptr:{path}",))


def diagnosis_active(path=None):
    return get_setting(f"diag:{path or active_path()}") == "1"


def start_diagnosis(path=None):
    """Diagnoza poziomu na życzenie ucznia (pytania z różnych tematów)."""
    path = path or active_path()
    set_setting(f"diag:{path}", "1")
    clear_pointer(path)


def reset_path(path=None):
    """Kasuje oceny tej ścieżki: nauka zaczyna się od pierwszego tematu."""
    path = path or active_path()
    for (tid,) in _rows("SELECT id FROM topics WHERE path = ?", (path,)):
        _run("DELETE FROM mastery WHERE topic_id = ?", (tid,))
        _run("DELETE FROM events WHERE topic_id = ?", (tid,))
    clear_pointer(path)
    set_setting(f"diag:{path}", "0")


def _reassessed(topic_id, base_event):
    """Czy temat dostał po wyborze ucznia ocenę 'opanowany'."""
    return bool(_rows(
        "SELECT 1 FROM events WHERE topic_id = ? AND id > ? AND level >= ? LIMIT 1",
        (topic_id, base_event, MASTERED),
    ))


def _placement(ts):
    """Krok diagnozy (wyszukiwanie binarne) albo None, gdy front wiedzy znany."""
    n = len(ts)
    lo, hi = -1, n
    for i, t in enumerate(ts):
        lvl = t["level"]
        if lvl is None:
            continue
        if lvl >= MASTERED:
            lo = i
        elif hi == n:
            hi = i
    unknown = list(range(lo + 1, hi))
    if not unknown:
        return None
    return {"mode": "placement", "topic": ts[unknown[len(unknown) // 2]], "total": n}


def recommend(path=None):
    """Wybiera następny krok nauki. Domyślnie idziemy PO KOLEI.

    1. Diagnoza poziomu (tylko gdy uczeń o nią poprosił): pytania z różnych
       tematów, wyszukiwanie binarne; po znalezieniu frontu wiedzy wracamy do
       nauki po kolei.
    2. Wskaźnik ucznia (wybrał temat): uczymy tego tematu, a po jego
       opanowaniu idziemy do następnego nieopanowanego w kolejności.
    3. W przeciwnym razie: pierwszy nieopanowany temat ścieżki.
    Zwraca dict: mode ('placement' | 'teach' | 'done'), topic, total.
    """
    path = path or active_path()
    ts = get_topics(path)
    n = len(ts)
    if n == 0:
        return {"mode": "done", "topic": None, "total": 0}
    pos = {t["id"]: i for i, t in enumerate(ts)}

    if diagnosis_active(path):
        step = _placement(ts)
        if step:
            return step
        set_setting(f"diag:{path}", "0")
        clear_pointer(path)

    ptr = get_pointer(path)
    if ptr and ptr[0] in pos:
        tid, base = ptr
        i = pos[tid]
        if not _reassessed(tid, base):
            return _teach(ts, i)
        nxt = next((j for j in range(i + 1, n) if not _mastered(ts[j])), None)
        if nxt is not None:
            set_pointer(path, ts[nxt]["id"])
            return _teach(ts, nxt)
        clear_pointer(path)

    first = next((j for j, t in enumerate(ts) if not _mastered(t)), None)
    if first is None:
        return {"mode": "done", "topic": None, "total": n}
    return _teach(ts, first)


def next_step_text(path=None):
    rec = recommend(path)
    t = rec["topic"]
    if rec["mode"] == "done":
        return ("Ścieżka ukończona. Pogratuluj uczniowi i zaproponuj powtórki "
                "lub dodanie nowego kursu.")
    scope = f" Zakres: {t['details']}." if t["details"] else ""
    if rec["mode"] == "placement":
        return (
            f"TRYB DIAGNOZA. Sprawdź wiedzę z tematu [id={t['id']}] {t['title']} "
            f"(kategoria: {t['category']}).{scope} Zadaj JEDNO krótkie zadanie lub "
            "pytanie. Nie ucz z góry, nie dawaj wskazówek przed odpowiedzią. To diagnoza zamówiona przez ucznia: pytania z różnych tematów są zamierzone."
        )
    current = ""
    if t["level"] is not None:
        current = (f" Dotychczasowy wynik: {t['level']}/100. Wyjaśnij inaczej "
                   "niż poprzednio i daj nowe zadanie.")
    if rec.get("block_start"):
        return (
            f"TRYB NAUKA, POCZĄTEK BLOKU „{rec['block']}”. Zacznij od podstaw "
            "tego bloku, zakładając, że uczeń nie ma w nim żadnej wiedzy: "
            "najpierw 2-3 zdania, czego nauczy się w tym bloku i po co, potem "
            "najważniejsze pojęcia od zera na prostym przykładzie. Dopiero "
            f"potem temat do opanowania: [id={t['id']}] {t['title']} "
            f"(kategoria: {t['category']}).{scope}{current} "
            "Daj JEDNO, najprostsze zadanie. Ucz wyłącznie tego tematu."
        )
    return (
        f"TRYB NAUKA. Temat do opanowania: [id={t['id']}] {t['title']} "
        f"(kategoria: {t['category']}).{scope}{current} Wyjaśnij krótko, "
        "potem daj JEDNO zadanie. Ucz wyłącznie tego tematu, nie przeskakuj do innych."
    )


def teacher_context(path=None):
    """Tekst dopisywany do promptu systemowego: stan wiedzy i zalecany krok."""
    path = path or active_path()
    ts = get_topics(path)
    mastered = [t for t in ts if t["level"] is not None and t["level"] >= MASTERED]
    partial = [t for t in ts if t["level"] is not None and t["level"] < MASTERED]
    lines = ["", "",
             f"STAN NAUKI UCZNIA. Ścieżka: {path}. "
             f"Opanowane: {len(mastered)}/{len(ts)} tematów."]
    if mastered:
        lines.append("Opanowane (ostatnie): "
                     + "; ".join(t["title"] for t in mastered[-12:]) + ".")
    if partial:
        lines.append("Ćwiczone, jeszcze nieopanowane: "
                     + "; ".join(f"{t['title']} ({t['level']}/100)"
                                 for t in partial[:8]) + ".")
    events = recent_events(path, 3)
    if events:
        lines.append("Ostatnie oceny: " + "; ".join(
            f"{e['title']} -> {e['level']}/100 ({e['evidence']})" for e in events
        ) + ".")
    lines.append(next_step_text(path))
    return "\n".join(lines)


# ---------- kursy (np. Udemy) ----------
SECTION_RE = re.compile(
    r"^(section|sekcja|rozdział|moduł|module|chapter)\s+\d+\s*[:.\-–]?\s*(.*)$",
    re.I,
)
LEAD_RE = re.compile(
    r"^\s*(?:(?:lecture|wykład|lekcja)\s+)?\d+\s*[\.\):]\s+|^\s*[-•*]\s+", re.I
)
TAIL_RE = re.compile(
    r"[\s\-–|•]*\b\d{1,2}:\d{2}(?::\d{2})?\s*$"
    r"|[\s\-–|•]*\b\d+\s*(?:min|godz|hr|sek)\b\.?\s*$",
    re.I,
)
SKIP_RE = re.compile(
    r"^(?:\d+\s*(?:lectures?|wykład\w*|lekcj\w*)\b.*|preview|podgląd"
    r"|resources?|zasoby|\d+\s*/\s*\d+.*)$",
    re.I,
)


def parse_toc(text):
    """Rozbija wklejony spis treści kursu na sekcje.

    Zwraca listę (tytuł_sekcji, [lekcje]). Obsługuje format kopiowany ze
    strony Udemy ('Section 1: ...', czasy trwania, 'Preview'). Gdy w tekście
    nie ma nagłówków sekcji, każda lekcja staje się osobnym tematem.
    """
    sections = []
    loose = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        m = SECTION_RE.match(line)
        if m:
            sections.append([(m.group(2).strip() or line)[:120], []])
            continue
        line = LEAD_RE.sub("", line)
        line = TAIL_RE.sub("", line).strip(" -–|•")
        if len(line) < 3 or SKIP_RE.match(line) or re.fullmatch(r"[\d:\s./]+", line):
            continue
        line = line[:140]
        if sections:
            sections[-1][1].append(line)
        else:
            loose.append(line)
    if sections:
        if loose:  # lekcje sprzed pierwszego nagłówka
            sections.insert(0, ["Wprowadzenie", loose])
        return [(s, lec) for s, lec in sections]
    return [(lec, [lec]) for lec in loose]


def add_course(title, url, toc_text, provider="Udemy"):
    """Dodaje kurs jako nową ścieżkę nauki (sekcja = temat)."""
    title = " ".join((title or "").split())
    if not title:
        raise ValueError("Podaj tytuł kursu.")
    sections = parse_toc(toc_text)
    if not sections:
        raise ValueError("Nie znalazłem żadnych lekcji w wklejonym spisie treści.")
    path = f"{provider}: {title}"
    if path in list_paths():
        raise ValueError("Taki kurs jest już dodany.")
    _run(
        "INSERT INTO courses (title, provider, url, path, added) VALUES (?, ?, ?, ?, ?)",
        (title, provider, (url or "").strip(), path, _now()),
    )
    for pos, (section, lectures) in enumerate(sections, 1):
        details = "Lekcje: " + "; ".join(lectures[:12])
        _run(
            "INSERT INTO topics (path, category, title, details, position) "
            "VALUES (?, ?, ?, ?, ?)",
            (path, title, section, details[:600], pos),
        )
    return path, len(sections)


def list_courses():
    rows = _rows("SELECT title, provider, url, path, added FROM courses ORDER BY id")
    return [dict(title=r[0], provider=r[1], url=r[2], path=r[3], added=r[4])
            for r in rows]


def delete_course(path):
    if path == CORE_PATH:
        return
    for (tid,) in _rows("SELECT id FROM topics WHERE path = ?", (path,)):
        _run("DELETE FROM mastery WHERE topic_id = ?", (tid,))
        _run("DELETE FROM events WHERE topic_id = ?", (tid,))
    _run("DELETE FROM topics WHERE path = ?", (path,))
    _run("DELETE FROM courses WHERE path = ?", (path,))
    if get_setting("active_path") == path:
        set_setting("active_path", CORE_PATH)


init_db()
