# 🐍 Python Tutor

Lokalny nauczyciel Pythona oparty na modelu AI. Sprawdza, co już umiesz, prowadzi Cię
po ścieżce nauki blok po bloku i pokazuje postępy w panelu ucznia. Kod ucznia jest
uruchamiany w odizolowanym kontenerze Dockera.

## Najważniejsze funkcje

- **Nauczyciel, nie tylko czat.** Agent diagnozuje wiedzę, uczy wskazanego tematu,
  zadaje zadania, sprawdza je testami i nie podaje gotowych rozwiązań.
- **Ocenę opanowania zapisuje agent**, a nie uczeń. Każda ocena (0-100) ma
  uzasadnienie widoczne w panelu.
- **Każdy nowy blok zaczyna się od podstaw.**
- **Panel ucznia:** pierścień postępu, radar umiejętności, słupki kategorii,
  kafelki tematów i lista ostatnich ocen.
- **Kursy z Udemy:** wklejasz spis treści, a sekcje kursu stają się osobną ścieżką nauki.
- **Wieloliniowy edytor kodu** z przyciskami "Sprawdź rozwiązanie" i "Uruchom kod".
- **Działa lokalnie i za darmo** (Ollama), albo z dowolnym API zgodnym z OpenAI.

## Wymagania

| Składnik | Po co | Uwagi |
|---|---|---|
| Python 3.8+ | aplikacja | biblioteki: `openai`, `streamlit` |
| [Ollama](https://ollama.com) | lokalny model AI | domyślnie `qwen2.5:14b` (ok. 9 GB) |
| [Docker Desktop](https://www.docker.com) | piaskownica na kod ucznia | obraz `python:3.12-slim` |

Model 14B mieści się w całości na karcie z 12 GB VRAM. Mniejsze modele (7B) gorzej
radzą sobie z polszczyzną i wywoływaniem narzędzi.

## Instalacja (Windows, PowerShell)

```powershell
# 1. Biblioteki
pip install openai streamlit

# 2. Model (po instalacji Ollamy; otwórz nowe okno PowerShella)
ollama pull qwen2.5:14b

# 3. Dłuższy kontekst dla Ollamy (potem zamknij Ollamę w zasobniku i uruchom ją ponownie)
setx OLLAMA_CONTEXT_LENGTH 8192

# 4. Obraz dla piaskownicy (Docker Desktop musi być uruchomiony: "Engine running")
docker pull python:3.12-slim
```

Motyw nie wymaga konfiguracji: aplikacja dopasowuje się do motywu Streamlita (jasny lub ciemny,
domyślnie według ustawień systemu).

## Uruchomienie

Przejdź do folderu projektu (ścieżkę ze spacjami weź w cudzysłów) i wystartuj aplikację:

```powershell
cd "S:\python projects\Nowy folder"
python -m streamlit run app.py
```

Aplikacja otworzy się pod adresem <http://localhost:8501>. Przed każdą nauką
sprawdź, czy działają **Ollama** i **Docker Desktop**.

Wersja terminalowa, bez interfejsu (nie wymaga Dockera, ale uruchamianie kodu
zwróci błąd): `python agent.py`.

## Wygląd

Interfejs jest stonowany i wzorowany na platformach edukacyjnych: neutralna paleta z jednym
niebieskim akcentem, płaskie karty z cienką ramką, czcionka Inter i ikony liniowe zamiast emoji.

- **jasny pasek boczny**: logo, menu z ikonami (Panel, Nauczyciel, Kursy) z wyraźnie zaznaczoną
  aktywną pozycją, wybór ścieżki, karta bieżącej ścieżki z postępem i następnym tematem oraz
  informacja o używanym modelu,
- **górny pasek** z nawigacją okruszkową i aktywną ścieżką,
- **panel**: karta "Kontynuuj naukę", wykresy i program ścieżki podzielony na bloki,
- **widok nauczyciela**: nagłówek bieżącego tematu z postępem bloku, wybór lekcji i po prawej
  lista wszystkich tematów (jak spis lekcji w kursie),
- **katalog kursów** w formie kart z postępem.

**Jasny i ciemny motyw.** Elementy Streamlita zostają w jego motywie, a nasze karty dziedziczą
kolor tekstu z motywu i mają półprzezroczyste tła, więc tekst i tło zawsze mają kontrast.
Panel i lista programu (osobne ramki HTML) wykrywają motyw po kolorze tła aplikacji i przełączają
jasną lub ciemną paletę (kontrast tekstu co najmniej 4,5:1).
Jeśli chcesz wymusić motyw, utwórz plik `.streamlit\config.toml` z zawartością `[theme]` i `base = "light"`
(lub `"dark"`).

Paleta i kształty są w zmiennych `:root` na początku CSS w `ui.py` (np. `--accent`).
Przyciski mają ikony Material
(`st.button(icon=...)`), a menu boczne to przyciski stylizowane na listę nawigacji.
Elementy Streamlita są stylizowane przez selektory CSS, które mogą się zmienić w nowszych
wersjach Streamlita. W razie potrzeby wystarczy je poprawić w `ui.py`.

## Jak korzystać

Aplikacja ma trzy strony (menu po lewej):

1. **🏠 Panel.** Podsumowanie nauki i karta z następnym krokiem. Przycisk
   "Kontynuuj" przenosi do nauczyciela.
2. **🎓 Nauczyciel.** Rozmowa z agentem. Sam wybierasz, czego się uczysz:
   - **lista lekcji + "▶ Zacznij ten temat"**: nauczyciel uczy dokładnie tej lekcji
     (nowa rozmowa), a po jej opanowaniu przechodzi do następnej nieopanowanej po kolei,
   - **"⏮ Od początku"**: po potwierdzeniu kasuje oceny tej ścieżki i zaczyna od pierwszego tematu,
   - **"▶ Kontynuuj"**: wznawia bieżący temat,
   - **"🔍 Diagnoza poziomu"**: krótkie pytania z różnych tematów, żeby ustalić, co już umiesz.
     Tylko wtedy nauczyciel skacze po tematach.

   W edytorze kodu wklejasz rozwiązanie:
   - **✅ Sprawdź rozwiązanie**: nauczyciel pisze własne testy (także brzegowe) i je uruchamia,
   - **▶️ Uruchom kod**: kod uruchamia się w Dockerze, a nauczyciel wyjaśnia wynik lub błąd.
   - Wcięcia rób spacjami. Klawisz Tab w przeglądarce przenosi kursor zamiast wstawiać wcięcie.
   - "Nowa rozmowa" czyści czat. Postępy zostają.
3. **📚 Kursy.** Lista ścieżek nauki, przełączanie aktywnej ścieżki i dodawanie
   kursów z Udemy.

### Dodawanie kursu z Udemy

1. Na stronie kursu rozwiń **Zawartość kursu** (*Course content*) i wszystkie sekcje.
2. Zaznacz całą listę, skopiuj ją i wklej w zakładce **Kursy**, wpisując tytuł kursu.
3. Sprawdź podgląd rozpoznanych sekcji i kliknij **Dodaj kurs**.

Każda sekcja staje się tematem, a lekcje z niej opisem zakresu. Automatyczne pobieranie
spisu z Udemy nie jest zaimplementowane (strona jest chroniona przed botami).

## Jak działa nauczanie

- **Ścieżka** to uporządkowana lista tematów. Wbudowana ścieżka "Python od zera"
  ma 30 tematów w 7 blokach (podstawy, sterowanie, struktury danych, funkcje,
  moduły i pliki, programowanie obiektowe, jakość kodu).
- **Domyślnie po kolei.** Nauczyciel uczy pierwszego nieopanowanego tematu ścieżki
  i nie przeskakuje do innych. Jeśli wybierzesz temat sam, uczy właśnie jego, a po
  opanowaniu idzie dalej po kolei od tego miejsca. Pominięte tematy nadal czekają
  na swoją kolej.
- **Diagnoza na życzenie.** Dopiero po kliknięciu "Diagnoza poziomu" nauczyciel pyta o tematy
  ze środka niezbadanego zakresu (wyszukiwanie binarne), więc wystarcza kilka krótkich
  pytań. Wtedy też, i tylko wtedy, opanowanie trudniejszego tematu zalicza wcześniejsze
  nieocenione tematy jako "wywnioskowane" (w panelu są oznaczone). Po diagnozie nauka
  wraca do trybu po kolei.
- **Nauka.** Przy porażce nauczyciel tłumaczy inaczej i daje nowe zadanie z tego samego tematu.
- **Start bloku od podstaw.** Gdy dochodzisz do bloku, w którym nie pokazałeś jeszcze
  własnej wiedzy (ocena bezpośrednia co najmniej 50), nauczyciel zaczyna od przeglądu
  bloku, pojęć od zera i najprostszego zadania. W kursie z Udemy blokiem jest każda sekcja.
- **Skala ocen.** 80 i więcej = opanowany (samodzielne rozwiązanie, testy przeszły,
  bez podpowiedzi z kodem). 50-79 = z podpowiedziami lub drobnymi błędami.
  Poniżej 50 = nie radzi sobie.
- **Podpowiedzi** są stopniowe: najpierw koncepcja, potem pseudokod, a fragment kodu
  tylko na wyraźną prośbę.

## Struktura projektu

| Plik | Zawartość |
|---|---|
| `app.py` | interfejs Streamlit (panel, nauczyciel, kursy) |
| `agent.py` | pętla agenta, narzędzia, piaskownica Dockera, prompt nauczyciela |
| `knowledge.py` | baza SQLite: tematy, oceny, silnik diagnozy i nauki, import kursów |
| `dashboard.py` | panel ucznia (HTML z wykresami) i lista programu ścieżki |
| `ui.py` | wspólny wygląd: CSS aplikacji oraz karty, pasek górny i nagłówek lekcji |
| `tutor.db` | **tworzy się sam**: wszystkie postępy, kursy i oceny |

## Konfiguracja

Zmienne środowiskowe (w PowerShellu ustawiasz je tylko dla bieżącego okna):

| Zmienna | Domyślnie | Znaczenie |
|---|---|---|
| `LLM_MODEL` | `qwen2.5:14b` | nazwa modelu |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | adres API zgodnego z OpenAI |
| `LLM_API_KEY` | `ollama` | klucz API (dla Ollamy dowolny tekst) |

```powershell
$env:LLM_MODEL="qwen3:14b"
python -m streamlit run app.py
```

Można też użyć darmowych planów dostawców z API zgodnym z OpenAI (np. Groq, Google Gemini):
ustaw `LLM_BASE_URL`, `LLM_API_KEY` i `LLM_MODEL` według dokumentacji dostawcy. Nazwy modeli
i limity się zmieniają, więc sprawdź aktualne wartości u dostawcy.

Stałe w kodzie, które możesz zmienić:

- `knowledge.py`: `MASTERED` (próg opanowania, domyślnie 80), `CORE_TOPICS` (lista tematów),
- `agent.py`: `MAX_STEPS` (limit kroków pętli), `KEEP_MESSAGES` (ile ostatnich wiadomości trafia
  do modelu) i `SYSTEM` (prompt nauczyciela).

> Lista `CORE_TOPICS` trafia do bazy tylko raz, przy pierwszym uruchomieniu. Po jej zmianie
> usuń `tutor.db` (przy zatrzymanej aplikacji), żeby baza zbudowała się od nowa. Usunięcie
> pliku kasuje też wszystkie postępy i dodane kursy.

## Bezpieczeństwo piaskownicy

Kod ucznia działa w kontenerze `python:3.12-slim` z ograniczeniami: bez sieci
(`--network none`), 128 MB RAM, 0,5 CPU, limit 64 procesów, system plików tylko do
odczytu (zapis wyłącznie w `/tmp`), użytkownik bez uprawnień roota i limit 5 sekund
na uruchomienie. Z tego powodu kod ucznia nie może instalować pakietów ani pobierać
danych z internetu, a `input()` zwraca błąd, bo kontener nie ma wejścia.

## Rozwiązywanie problemów

| Objaw | Przyczyna i rozwiązanie |
|---|---|
| `File does not exist: app.py` albo `No module named 'agent'` | terminal jest w złym folderze: przejdź `cd` do folderu z plikami |
| `streamlit` nie jest rozpoznawane | uruchamiaj przez `python -m streamlit run app.py` |
| `ollama` / `docker` nie jest rozpoznawane | program nie jest zainstalowany albo terminal otwarty przed instalacją: zainstaluj i otwórz nowe okno |
| `failed to connect to the docker API` albo komunikat "Docker nie działa" | uruchom Docker Desktop i poczekaj na "Engine running" |
| Błąd połączenia z modelem | Ollama nie działa lub model nie jest pobrany: `ollama list`, w razie braku `ollama pull qwen2.5:14b` |
| Odpowiedzi w obcym języku, "zapominanie" zasad | za krótki kontekst: sprawdź `ollama ps` w trakcie rozmowy (CONTEXT powinien wynosić 8192), ustaw `OLLAMA_CONTEXT_LENGTH` i zrestartuj Ollamę, potem odśwież stronę |
| W czacie pojawia się surowy JSON z `tool_call` | zdarza się modelom lokalnym: aplikacja zwykle wykrywa to sama, a jeśli nie, kliknij "Nowa rozmowa" lub spróbuj innego modelu |
| Ocena nie pojawia się w panelu | model pominął zapis: napisz mu "zapisz ocenę" |
| Odpowiedzi są wolne | `ollama ps` powinno pokazywać `100% GPU`; przy podziale GPU/CPU model lub kontekst jest za duży |

Szybka kontrola, czy model działa na karcie: w drugim oknie PowerShella wpisz `ollama ps`
w trakcie rozmowy z nauczycielem.

## Ograniczenia

- Ocenia lokalny model, więc bywa zbyt łaskawy lub zbyt surowy. Uzasadnienia ocen są
  widoczne w panelu, żeby można było je zweryfikować.
- Ścieżki są liniowe (kolejność tematów = kolejność zależności), bez pełnego grafu zależności
  i bez powtórek w odstępach czasu.
- Import kursu działa przez wklejenie spisu treści. Agent zna tytuły sekcji i lekcji,
  ale nie ich treść.
- Z aplikacji nie da się ręcznie zmienić oceny tematu.
- Czcionka Inter jest pobierana z Google Fonts. Bez internetu aplikacja użyje czcionki systemowej.
