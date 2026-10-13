"""Python Tutor: panel ucznia + nauczyciel AI.
Uruchom: python -m streamlit run app.py"""
import streamlit as st
import streamlit.components.v1 as components

import knowledge as kb
import ui
from agent import MODEL, ask, run_python
from dashboard import build_dashboard, build_outline

st.set_page_config(page_title="Python Tutor", page_icon="🐍", layout="wide")
ui.apply_theme()

# (etykieta, ikona Material)
NAV = [("Panel", "dashboard"), ("Nauczyciel", "school"), ("Kursy", "menu_book")]
PAGE_TITLES = {"Panel": "Panel", "Nauczyciel": "Nauczyciel", "Kursy": "Kursy i ścieżki"}
if st.session_state.get("page") not in PAGE_TITLES:
    st.session_state.page = "Panel"
if "history" not in st.session_state:
    st.session_state.history = []  # wiadomości dla API
    st.session_state.chat = []     # wiadomości do wyświetlenia


def goto(page):
    st.session_state.page = page


def btn(container, label, icon=None, **kw):
    """Przycisk z ikoną Material; w razie problemu z ikoną działa bez niej."""
    if icon:
        try:
            return container.button(label, icon=f":material/{icon}:", **kw)
        except Exception:
            pass
    return container.button(label, **kw)


# ---------- pasek boczny ----------
with st.sidebar:
    st.markdown(ui.brand_html(), unsafe_allow_html=True)
    st.markdown('<div class="side-label">Nauka</div>', unsafe_allow_html=True)
    for label, icon in NAV:
        btn(st, label, icon, key=f"nav_{label}", use_container_width=True,
            type="primary" if st.session_state.page == label else "secondary",
            on_click=goto, args=(label,))

    st.markdown('<div class="side-label">Aktualna ścieżka</div>', unsafe_allow_html=True)
    paths = kb.list_paths()
    active = kb.active_path()
    choice = st.selectbox("Ścieżka nauki", paths, index=paths.index(active),
                          label_visibility="collapsed")
    if choice != active:
        kb.set_setting("active_path", choice)
        st.rerun()
    stats = kb.path_stats(choice)
    st.markdown(ui.sidebar_course_html(choice, stats, kb.recommend(choice)),
                unsafe_allow_html=True)
    st.markdown(ui.sidebar_footer_html(MODEL), unsafe_allow_html=True)

st.markdown(ui.topbar_html(PAGE_TITLES[st.session_state.page], choice, stats),
            unsafe_allow_html=True)

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))


# ---------- strona: panel ----------
def page_dashboard():
    path = kb.active_path()
    rec = kb.recommend(path)
    c1, c2 = st.columns([5, 1.4], gap="medium")
    c1.markdown(ui.hero_html(rec, kb.path_stats(path)), unsafe_allow_html=True)
    with c2:
        st.markdown('<div style="height:44px"></div>', unsafe_allow_html=True)
        btn(st, "Kontynuuj naukę", "play_arrow", type="primary", use_container_width=True,
            on_click=goto, args=("Nauczyciel",))
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    doc, height = build_dashboard(path)
    components.html(doc, height=height, scrolling=True)


# ---------- strona: nauczyciel ----------
def reset_chat():
    st.session_state.history = []
    st.session_state.chat = []


def cb_start_topic(path):
    kb.set_pointer(path, st.session_state.pick_topic)
    reset_chat()
    st.session_state.auto_prompt = "Zacznij ten temat."


def cb_ask_reset():
    st.session_state.confirm_reset = True


def cb_cancel_reset():
    st.session_state.confirm_reset = False


def cb_do_reset(path):
    kb.reset_path(path)
    reset_chat()
    st.session_state.confirm_reset = False
    st.session_state.auto_prompt = "Zacznij od początku."


def cb_diagnosis(path):
    kb.start_diagnosis(path)
    reset_chat()
    st.session_state.auto_prompt = "Sprawdź mój poziom."


def page_teacher():
    path = kb.active_path()
    quick = st.session_state.pop("auto_prompt", None)
    code_prompt = None

    topics = kb.get_topics(path)
    ids = [t["id"] for t in topics]
    labels = {}
    for t in topics:
        if t["level"] is not None and t["level"] >= kb.MASTERED:
            mark = "✓"
        elif t["level"] is not None:
            mark = "◐"
        else:
            mark = "○"
        labels[t["id"]] = f"{mark}  {t['category']} · {t['title']}"
    current = kb.recommend(path)["topic"]
    if st.session_state.get("pick_topic") not in ids:
        st.session_state.pick_topic = current["id"] if current else ids[0]

    left, right = st.columns([5, 2], gap="large")

    with left:
        st.markdown(ui.lesson_head_html(path), unsafe_allow_html=True)

        a1, a2, a3 = st.columns([3.6, 1.7, 1.7])
        a1.selectbox("Wybierz lekcję", ids, key="pick_topic",
                     format_func=lambda i: labels[i], label_visibility="collapsed")
        btn(a2, "Zacznij ten temat", "play_arrow", type="primary", use_container_width=True,
            on_click=cb_start_topic, args=(path,), key="start_topic")
        btn(a3, "Od początku", "restart_alt", use_container_width=True,
            on_click=cb_ask_reset, key="ask_reset")

        if st.session_state.get("confirm_reset"):
            st.warning("Skasuję oceny tej ścieżki i zaczniemy od pierwszego tematu. "
                       "Tej operacji nie można cofnąć.")
            w1, w2 = st.columns(2)
            btn(w1, "Tak, zresetuj postępy", "restart_alt", type="primary",
                use_container_width=True, on_click=cb_do_reset, args=(path,), key="do_reset")
            btn(w2, "Anuluj", "close", use_container_width=True,
                on_click=cb_cancel_reset, key="cancel_reset")

        b1, b2, b3, b4 = st.columns(4)
        if btn(b1, "Kontynuuj", "play_circle", use_container_width=True, key="b_continue"):
            quick = "Kontynuuj naukę."
        if btn(b2, "Podpowiedź", "lightbulb", use_container_width=True, key="b_hint"):
            quick = "Daj mi kolejną podpowiedź do tego zadania."
        btn(b3, "Diagnoza", "fact_check", use_container_width=True, key="b_diag",
            on_click=cb_diagnosis, args=(path,),
            help="Krótkie pytania z różnych tematów, żeby ustalić, co już umiesz")
        if btn(b4, "Nowa rozmowa", "add_comment", use_container_width=True, key="b_new"):
            reset_chat()
            st.rerun()

        if not st.session_state.chat:
            st.info("Kliknij „Kontynuuj”. Nauczyciel poprowadzi Cię po kolei przez materiał, "
                    "a temat możesz też wybrać sam z listy powyżej.")
        for role, text in st.session_state.chat:
            st.chat_message(role).write(text)

        # edytor kodu (wieloliniowy)
        st.markdown(
            "<style>div[data-testid='stTextArea'] textarea "
            "{font-family: Consolas, 'Courier New', monospace;}</style>",
            unsafe_allow_html=True,
        )
        with st.expander("Edytor kodu", expanded=True):
            code = st.text_area(
                "Wklej lub napisz kod (wcięcia rób spacjami, nie klawiszem Tab)",
                key="code_editor",
                height=220,
            )
            c1, c2 = st.columns(2)
            do_check = btn(c1, "Sprawdź rozwiązanie", "task_alt", use_container_width=True,
                           key="b_check")
            do_run = btn(c2, "Uruchom kod", "play_arrow", use_container_width=True,
                         key="b_run")

        if (do_check or do_run) and not code.strip():
            st.warning("Edytor jest pusty.")
        elif do_check:
            code_prompt = (
                "Sprawdź moje rozwiązanie przez check_solution, z własnymi testami:\n"
                "```python\n" + code.strip("\n") + "\n```"
            )
        elif do_run:
            with st.spinner("Uruchamiam kod..."):
                output = run_python(code)
            if output.startswith("Błąd: Docker"):
                st.error(output)  # nie wysyłamy tego do nauczyciela
            else:
                code_prompt = (
                    "Uruchomiłem mój kod.\nKod:\n```python\n" + code.strip("\n") + "\n```\n"
                    "Wynik:\n```\n" + output + "\n```\n"
                    "Wyjaśnij wynik lub błąd, nie dawaj gotowego rozwiązania."
                )

    with right:
        components.html(build_outline(path), height=700, scrolling=True)

    typed = st.chat_input("Napisz do nauczyciela...")
    prompt = code_prompt or quick or typed

    if prompt:
        with left:
            st.chat_message("user").write(prompt)
        st.session_state.chat.append(("user", prompt))

        history = st.session_state.history
        start = len(history)  # do cofnięcia w razie błędu
        history.append({"role": "user", "content": prompt})

        try:
            with left:
                with st.spinner("Nauczyciel myśli..."):
                    answer = ask(history)
        except Exception as e:
            del history[start:]  # unikamy "wiszącego" tool_use w historii
            answer = f"⚠️ Błąd: {e}"

        st.session_state.chat.append(("assistant", answer))
        st.rerun()


# ---------- strona: kursy ----------
def add_course_cb():
    try:
        path, n = kb.add_course(
            st.session_state.c_title, st.session_state.c_url, st.session_state.c_toc
        )
    except ValueError as e:
        st.session_state.c_error = str(e)
        return
    kb.set_setting("active_path", path)
    st.session_state.flash = (
        f"Dodano kurs „{st.session_state.c_title.strip()}”: {n} tematów. "
        "Ustawiono go jako aktywną ścieżkę nauki."
    )
    st.session_state.c_title = ""
    st.session_state.c_url = ""
    st.session_state.c_toc = ""


def page_courses():
    active = kb.active_path()
    courses = {c["path"]: c for c in kb.list_courses()}
    all_paths = kb.list_paths()

    st.markdown('<div class="sect" style="margin-top:0">Moje ścieżki i kursy</div>',
                unsafe_allow_html=True)
    for start in range(0, len(all_paths), 3):
        cols = st.columns(3, gap="large")
        for j, path in enumerate(all_paths[start:start + 3]):
            i = start + j
            with cols[j]:
                st.markdown(ui.course_card_html(path, path == active, path in courses),
                            unsafe_allow_html=True)
                b1, b2 = st.columns([3, 1.6])
                if path != active:
                    btn(b1, "Ustaw jako aktywną", "check", key=f"use_{i}",
                        use_container_width=True, on_click=kb.set_setting,
                        args=("active_path", path))
                else:
                    btn(b1, "Aktywna", "check_circle", key=f"act_{i}", disabled=True,
                        use_container_width=True)
                if path in courses:
                    btn(b2, "Usuń", "delete", key=f"del_{i}", use_container_width=True,
                        help="Usuń kurs i jego postępy",
                        on_click=kb.delete_course, args=(path,))

    st.markdown('<div class="sect">Dodaj nowy kurs</div>', unsafe_allow_html=True)
    with st.expander("Dodaj kurs z Udemy", expanded=not courses):
        left, right = st.columns([3, 2], gap="large")
        with left:
            if "c_error" in st.session_state:
                st.error(st.session_state.pop("c_error"))
            title = st.text_input("Tytuł kursu", key="c_title")
            st.text_input("Link do kursu (opcjonalnie)", key="c_url")
            toc = st.text_area("Spis treści kursu (wklej)", key="c_toc", height=240)
            sections = kb.parse_toc(toc) if toc.strip() else []
            if toc.strip():
                lessons = sum(len(lec) for _, lec in sections)
                st.caption(f"Rozpoznano: {len(sections)} tematów (sekcji), {lessons} lekcji.")
                shown = "\n".join(f"- **{sec}** ({len(lec)} lekcji)" for sec, lec in sections[:12])
                more = f"\n- … i {len(sections) - 12} kolejnych" if len(sections) > 12 else ""
                st.markdown(shown + more)
            btn(st, "Dodaj kurs", "add", type="primary", key="b_add",
                disabled=not (title.strip() and sections), on_click=add_course_cb)
        with right:
            st.markdown(
                "**Jak skopiować spis treści?**\n\n"
                "1. Otwórz stronę kursu na Udemy i znajdź sekcję **Zawartość kursu** "
                "(*Course content*).\n"
                "2. Kliknij **Rozwiń wszystkie sekcje**.\n"
                "3. Zaznacz myszką całą listę, skopiuj i wklej obok.\n\n"
                "Każda sekcja kursu stanie się tematem, a lekcje z niej opisem tematu. "
                "Nauczyciel sprawdzi Twoją wiedzę z kolejnych sekcji i poprowadzi Cię "
                "przez nie po kolei."
            )


page = st.session_state.page
if page == "Panel":
    page_dashboard()
elif page == "Nauczyciel":
    page_teacher()
else:
    page_courses()
