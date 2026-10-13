"""Backend nauczyciela Pythona (Ollama / API zgodne z OpenAI).

Wymagania: pip install openai
Zmienne środowiskowe (opcjonalne, domyślnie Ollama lokalnie):
  LLM_BASE_URL, LLM_API_KEY, LLM_MODEL
Docker musi być uruchomiony, obraz: docker pull python:3.12-slim
Wiedza o uczniu: knowledge.py (baza SQLite tutor.db)
"""
import inspect
import json
import os
import re
import subprocess

from openai import OpenAI

from knowledge import next_step_text, set_mastery, teacher_context

MODEL = os.getenv("LLM_MODEL", "qwen2.5:14b")
MAX_STEPS = 8                # limit kroków pętli agenta
KEEP_MESSAGES = 30           # ile ostatnich wiadomości trafia do modelu

client = OpenAI(
    base_url=os.getenv("LLM_BASE_URL", "http://localhost:11434/v1"),
    api_key=os.getenv("LLM_API_KEY", "ollama"),
)

SYSTEM = """Jesteś nauczycielem Pythona, a rozmówca jest Twoim uczniem.
Nie tylko odpowiadasz na pytania: sprawdzasz, co uczeń umie, i prowadzisz go
najkrótszą drogą do opanowania materiału.
Odpowiadaj WYŁĄCZNIE po polsku, zwięźle, nigdy w innym języku.
Nigdy nie pisz wiadomości za ucznia i nie udawaj wywołań narzędzi:
gdy potrzebujesz narzędzia, wywołaj je naprawdę.

JAK UCZYSZ
1. W sekcji STAN NAUKI UCZNIA (na końcu tej instrukcji) masz stan wiedzy
   ucznia i zalecony krok. Trzymaj się go. Ucz wyłącznie wskazanego tematu
   i nie przeskakuj na własną rękę do innych tematów ani bloków. Jeśli
   uczeń zapyta o coś spoza tematu, odpowiedz krótko i wróć do tematu.
   Polecenia ucznia "Kontynuuj naukę", "Zacznij ten temat", "Zacznij od
   początku" i "Sprawdź mój poziom" oznaczają: działaj według zalecenia
   ze STAN NAUKI.
2. TRYB DIAGNOZA: sprawdzasz, czy uczeń zna wskazany temat. Zadaj JEDNO
   krótkie zadanie lub pytanie. W tym trybie nie uczysz i nie podpowiadasz
   przed odpowiedzią. Na początku powiedz uczniowi jednym zdaniem, że to
   krótka diagnoza i że niewiedza jest w porządku.
3. TRYB NAUKA: wyjaśnij wskazany temat krótko (kilka zdań i mały przykład),
   potem daj JEDNO zadanie z przykładem wejścia i wyjścia. Nazwij funkcję,
   którą uczeń ma napisać. Testów nie pokazuj.
   Każdy nowy blok zaczynasz od podstaw. Gdy w zaleceniu jest POCZĄTEK
   BLOKU: zero zakładanej wiedzy z tego bloku, proste słownictwo, pojęcia
   od zera na krótkich przykładach i najprostsze możliwe pierwsze zadanie.
   Tempo i trudność zwiększaj dopiero w kolejnych tematach bloku.
4. Gdy uczeń odeśle rozwiązanie, sprawdź je przez check_solution z własnymi
   testami (assert), także przypadkami brzegowymi. Nie podawaj gotowego
   rozwiązania. Gdy testy nie przejdą, daj wskazówkę. Podpowiedzi dawaj
   stopniowo: 1) koncepcja bez kodu, 2) szkic kroków (pseudokod), 3) fragment
   kodu dopiero na wyraźną prośbę.
5. Nie ufaj deklaracjom ("umiem to", "to proste"). Poziom oceniaj wyłącznie
   po tym, co uczeń faktycznie zrobił.
6. Po ocenie ZAWSZE wywołaj update_mastery(topic_id, level, evidence).
   topic_id weź z sekcji STAN NAUKI. level to 0-100:
   80 i więcej = uczeń rozwiązał zadanie samodzielnie, testy przeszły, bez
   podpowiedzi z kodem; 50-79 = poradził sobie z podpowiedziami lub z drobnymi
   błędami; poniżej 50 = nie radzi sobie. evidence to jedno zdanie po polsku
   o tym, co uczeń zrobił (uczeń zobaczy je w swoim panelu).
   Tematy czysto organizacyjne (wstęp, instalacja) możesz zaliczyć poziomem 80
   z adnotacją "temat organizacyjny".
7. Wynik update_mastery mówi, jaki jest następny krok. Powiedz uczniowi
   krótko, jak poszło i co dalej. Gdy temat jest nieopanowany, wyjaśnij go
   inaczej i daj nowe zadanie z tego samego tematu.
8. Gdy uczeń poda własny kod do sprawdzenia, uruchom go przez run_python
   i wyjaśnij wynik lub błąd.
9. Kod ucznia (z bloku ```python) przekazuj do narzędzi dokładnie w takiej
   postaci, w jakiej go dostałeś, bez żadnych zmian.
10. Wiadomość "Uruchomiłem mój kod" zawiera już wynik działania kodu: nie
    uruchamiaj go ponownie, tylko wyjaśnij wynik lub błąd.
"""

TOOLS = [
    {
        "name": "run_python",
        "description": "Uruchamia kod Pythona w piaskownicy i zwraca stdout/stderr.",
        "input_schema": {
            "type": "object",
            "properties": {"code": {"type": "string"}},
            "required": ["code"],
        },
    },
    {
        "name": "check_solution",
        "description": "Uruchamia rozwiązanie ucznia razem z testami (assert).",
        "input_schema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Kod ucznia"},
                "tests": {"type": "string", "description": "Testy z assert"},
            },
            "required": ["code", "tests"],
        },
    },
    {
        "name": "update_mastery",
        "description": (
            "Zapisuje ocenę opanowania tematu przez ucznia (0-100) wraz "
            "z uzasadnieniem. Wywołuj po każdej ocenie."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "topic_id": {"type": "integer", "description": "id tematu ze STAN NAUKI"},
                "level": {"type": "integer", "description": "0-100"},
                "evidence": {"type": "string", "description": "co uczeń zrobił"},
            },
            "required": ["topic_id", "level", "evidence"],
        },
    },
    {
        "name": "get_learning_state",
        "description": "Zwraca aktualny stan nauki ucznia i zalecony następny krok.",
        "input_schema": {"type": "object", "properties": {}},
    },
]

# Te same narzędzia w formacie OpenAI
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": t["name"],
            "description": t["description"],
            "parameters": t["input_schema"],
        },
    }
    for t in TOOLS
]


# ---------- ocena opanowania ----------
def update_mastery(topic_id, level, evidence=""):
    try:
        title = set_mastery(int(float(topic_id)), int(float(level)), str(evidence))
    except (ValueError, TypeError) as e:
        return f"Błąd: {e}. Użyj id tematu z sekcji STAN NAUKI."
    return f"Zapisano: {title} = {int(float(level))}/100.\n" + next_step_text()


def get_learning_state():
    return teacher_context()


# ---------- wykonywanie kodu w Dockerze ----------
DOCKER_DOWN_MSG = (
    "Błąd: Docker nie działa. Uruchom Docker Desktop i poczekaj, "
    "aż pokaże status 'Engine running'."
)


def run_python(code):
    cmd = [
        "docker", "run", "--rm",
        "--network", "none",     # brak internetu
        "--memory", "128m",      # limit RAM
        "--cpus", "0.5",         # limit CPU
        "--pids-limit", "64",    # ochrona przed fork bombą
        "--read-only",           # system plików tylko do odczytu
        "--tmpfs", "/tmp",       # jedyne miejsce do zapisu
        "--user", "65534",       # bez uprawnień roota
        "python:3.12-slim",
        "timeout", "5", "python", "-c", code,
    ]
    try:
        r = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            timeout=20, stdin=subprocess.DEVNULL,
        )
        if "docker API" in r.stderr or "docker daemon" in r.stderr.lower():
            return DOCKER_DOWN_MSG
        return (r.stdout + r.stderr) or "(brak wyjścia)"
    except subprocess.TimeoutExpired:
        return "Przekroczono limit czasu."
    except FileNotFoundError:
        return "Błąd: nie znaleziono polecenia docker. Czy Docker jest zainstalowany i uruchomiony?"


def check_solution(code, tests):
    full = code + "\n\n" + tests + "\nprint('WSZYSTKIE TESTY OK')"
    return run_python(full)


DISPATCH = {
    "run_python": run_python,
    "check_solution": check_solution,
    "update_mastery": update_mastery,
    "get_learning_state": get_learning_state,
}


def call_tool(name, args):
    func = DISPATCH.get(name)
    if func is None:
        return f"Nieznane narzędzie: {name}"
    # model czasem dodaje nieistniejące argumenty - odrzucamy je
    allowed = inspect.signature(func).parameters
    args = {k: v for k, v in args.items() if k in allowed}
    try:
        return func(**args)
    except Exception as e:  # błąd narzędzia nie może wywrócić agenta
        return f"Błąd narzędzia {name}: {e}"


# ---------- pętla agenta ----------
THINK_RE = re.compile(r"<think>.*?</think>", re.S)
TAG_RE = re.compile(r"</?tool_call>")


def extract_leaked_call(text):
    """Model czasem wypisuje wywołanie narzędzia jako zwykły tekst
    zamiast użyć mechanizmu narzędzi. Wyciągamy je z tekstu."""
    m = re.search(r'\{\s*"name"', text)
    if not m:
        return None
    try:
        obj, _ = json.JSONDecoder().raw_decode(text[m.start():])
    except json.JSONDecodeError:
        return None
    name = obj.get("name") if isinstance(obj, dict) else None
    if name not in DISPATCH:
        return None
    args = obj.get("arguments", {})
    return name, (args if isinstance(args, dict) else {})


def trimmed(history):
    """Ostatnie wiadomości; zawsze zaczynamy od wiadomości ucznia,
    żeby nie zostawić 'wiszącego' wyniku narzędzia."""
    msgs = history[-KEEP_MESSAGES:]
    while msgs and msgs[0]["role"] != "user":
        msgs = msgs[1:]
    return msgs


def ask(history):
    """Dopisuje odpowiedzi do history i zwraca tekst nauczyciela."""
    for step in range(MAX_STEPS):
        # stan wiedzy czytamy z bazy przy każdym kroku, więc jest aktualny
        system = SYSTEM + teacher_context()
        reply = client.chat.completions.create(
            model=MODEL,
            max_tokens=2000,
            temperature=0.3,
            tools=OPENAI_TOOLS,
            messages=[{"role": "system", "content": system}] + trimmed(history),
        )
        msg = reply.choices[0].message
        content = THINK_RE.sub("", msg.content or "").strip()

        calls = []  # (id, nazwa, argumenty)
        for tc in msg.tool_calls or []:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append((tc.id, tc.function.name, args))

        if not calls:
            leaked = extract_leaked_call(content)
            if leaked:
                calls.append((f"call_{step}", leaked[0], leaked[1]))
                content = ""  # surowy tekst wywołania nie trafia do ucznia

        content = TAG_RE.sub("", content).strip()
        entry = {"role": "assistant", "content": content}
        if calls:
            entry["tool_calls"] = [
                {"id": cid, "type": "function",
                 "function": {"name": n,
                              "arguments": json.dumps(a, ensure_ascii=False)}}
                for cid, n, a in calls
            ]
        history.append(entry)

        if not calls:
            return content or "Model nie zwrócił odpowiedzi. Spróbuj ponownie."

        for cid, n, a in calls:
            history.append({
                "role": "tool",
                "tool_call_id": cid,
                "content": call_tool(n, a),
            })

    return "Przerwano: agent wykonał zbyt wiele kroków."


# ---------- wersja terminalowa (opcjonalnie) ----------
if __name__ == "__main__":
    hist = []
    while True:
        text = input("Ty: ")
        if text in ("q", "quit"):
            break
        hist.append({"role": "user", "content": text})
        print("Nauczyciel:", ask(hist))
