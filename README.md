# 🐍 Python Tutor

A local Python teacher powered by an AI model. It checks what you already know, guides you
through a learning path block by block, and shows your progress in a student dashboard.
The student's code runs in an isolated Docker container.

## Key features

- **A teacher, not just a chat.** The agent diagnoses your knowledge, teaches the chosen topic,
  assigns exercises, checks them with tests, and does not hand out ready-made solutions.
- **Mastery is rated by the agent**, not by the student. Every rating (0-100) comes with
  a justification visible in the dashboard.
- **Every new block starts from the basics.**
- **Student dashboard:** progress ring, skills radar, category bars,
  topic tiles, and a list of recent ratings.
- **Udemy courses:** paste the table of contents and the course sections become a separate learning path.
- **Multi-line code editor** with "Check solution" and "Run code" buttons.
- **Runs locally and for free** (Ollama), or with any OpenAI-compatible API.

## Requirements

| Component | Purpose | Notes |
|---|---|---|
| Python 3.8+ | the application | libraries: `openai`, `streamlit` |
| [Ollama](https://ollama.com) | local AI model | default `qwen2.5:14b` (approx. 9 GB) |
| [Docker Desktop](https://www.docker.com) | sandbox for the student's code | image `python:3.12-slim` |

The 14B model fits entirely on a card with 12 GB of VRAM. Smaller models (7B) handle Polish
and tool calling worse.

## Installation (Windows, PowerShell)

```powershell
# 1. Libraries
pip install openai streamlit

# 2. Model (after installing Ollama; open a new PowerShell window)
ollama pull qwen2.5:14b

# 3. Longer context for Ollama (then quit Ollama in the system tray and start it again)
setx OLLAMA_CONTEXT_LENGTH 8192

# 4. Image for the sandbox (Docker Desktop must be running: "Engine running")
docker pull python:3.12-slim
```

The theme needs no configuration: the app adapts to the Streamlit theme (light or dark,
by default following your system settings).

## Running

Go to the project folder (put a path containing spaces in quotes) and start the app:

```powershell
cd "S:\python projects\Nowy folder"
python -m streamlit run app.py
```

The app opens at <http://localhost:8501>. Before each study session,
make sure that **Ollama** and **Docker Desktop** are running.

Terminal version, without a graphical interface (does not require Docker, but running code
will return an error): `python agent.py`.

## Appearance

The interface is understated and modeled on educational platforms: a neutral palette with a single
blue accent, flat cards with a thin border, the Inter font, and line icons instead of emoji.

- **light sidebar**: logo, menu with icons (Dashboard, Teacher, Courses) with a clearly highlighted
  active item, path selection, a card for the current path with progress and the next topic, and
  information about the model in use,
- **top bar** with breadcrumb navigation and the active path,
- **dashboard**: a "Continue learning" card, charts, and the path curriculum divided into blocks,
- **teacher view**: a header with the current topic and block progress, a lesson picker, and on the right
  a list of all topics (like a course's lesson list),
- **course catalog** in the form of cards with progress.

**Light and dark theme.** Streamlit's own elements stay in its theme, and our cards inherit
the text color from the theme and have semi-transparent backgrounds, so text and background always have contrast.
The dashboard and the curriculum list (separate HTML frames) detect the theme from the app's background color and switch
between a light and a dark palette (text contrast of at least 4.5:1).
If you want to force a theme, create the file `.streamlit\config.toml` containing `[theme]` and `base = "light"`
(or `"dark"`).

The palette and shapes are in `:root` variables at the beginning of the CSS in `ui.py` (e.g. `--accent`).
Buttons have Material icons
(`st.button(icon=...)`), and the sidebar menu consists of buttons styled as a navigation list.
Streamlit's elements are styled with CSS selectors, which may change in newer
Streamlit versions. If needed, just fix them in `ui.py`.

## How to use

The app has three pages (menu on the left):

1. **🏠 Dashboard.** A summary of your learning and a card with the next step. The "Continue"
   button takes you to the teacher.
2. **🎓 Teacher.** A conversation with the agent. You choose what to learn yourself:
   - **lesson list + "▶ Start this topic"**: the teacher teaches exactly that lesson
     (new conversation), and after you master it moves on to the next unmastered one in order,
   - **"⏮ From the beginning"**: after confirmation, deletes the ratings of this path and starts from the first topic,
   - **"▶ Continue"**: resumes the current topic,
   - **"🔍 Level diagnosis"**: short questions from various topics to determine what you already know.
     Only then does the teacher jump between topics.

   In the code editor you paste your solution:
   - **✅ Check solution**: the teacher writes its own tests (including edge cases) and runs them,
   - **▶️ Run code**: the code runs in Docker, and the teacher explains the result or error.
   - Indent with spaces. The Tab key in the browser moves the cursor instead of inserting an indent.
   - "New conversation" clears the chat. Progress is kept.
3. **📚 Courses.** A list of learning paths, switching the active path, and adding
   Udemy courses.

### Adding a Udemy course

1. On the course page, expand **Course content** and all of its sections.
2. Select the whole list, copy it, and paste it in the **Courses** tab, entering the course title.
3. Check the preview of the recognized sections and click **Add course**.

Each section becomes a topic, and the lessons within it become the description of its scope. Automatic fetching
of the table of contents from Udemy is not implemented (the site is protected against bots).

## How the teaching works

- **A path** is an ordered list of topics. The built-in path "Python from scratch"
  has 30 topics in 7 blocks (basics, control flow, data structures, functions,
  modules and files, object-oriented programming, code quality).
- **In order by default.** The teacher teaches the first unmastered topic of the path
  and does not jump to others. If you choose a topic yourself, it teaches that one, and after
  you master it continues in order from that point. Skipped topics still wait
  for their turn.
- **Diagnosis on demand.** Only after you click "Level diagnosis" does the teacher ask about topics
  from the middle of the unexamined range (binary search), so a few short
  questions are enough. Then, and only then, mastering a harder topic counts
  earlier unrated topics as "inferred" (marked as such in the dashboard). After the diagnosis, learning
  returns to the in-order mode.
- **Learning.** On failure, the teacher explains in a different way and gives a new exercise on the same topic.
- **Block start from the basics.** When you reach a block in which you have not yet shown
  your own knowledge (a direct rating of at least 50), the teacher starts with an overview
  of the block, concepts from scratch, and the simplest exercise. In a Udemy course, each section is a block.
- **Rating scale.** 80 and above = mastered (solved independently, tests passed,
  no hints with code). 50-79 = with hints or minor errors.
  Below 50 = struggling.
- **Hints** are gradual: first the concept, then pseudocode, and a code snippet
  only on explicit request.

## Project structure

| File | Contents |
|---|---|
| `app.py` | Streamlit interface (dashboard, teacher, courses) |
| `agent.py` | agent loop, tools, Docker sandbox, teacher prompt |
| `knowledge.py` | SQLite database: topics, ratings, diagnosis and learning engine, course import |
| `dashboard.py` | student dashboard (HTML with charts) and the path curriculum list |
| `ui.py` | shared look: app CSS plus cards, top bar, and lesson header |
| `tutor.db` | **created automatically**: all progress, courses, and ratings |

## Configuration

Environment variables (in PowerShell you set them only for the current window):

| Variable | Default | Meaning |
|---|---|---|
| `LLM_MODEL` | `qwen2.5:14b` | model name |
| `LLM_BASE_URL` | `http://localhost:11434/v1` | address of the OpenAI-compatible API |
| `LLM_API_KEY` | `ollama` | API key (for Ollama any text works) |

```powershell
$env:LLM_MODEL="qwen3:14b"
python -m streamlit run app.py
```

You can also use the free plans of providers with an OpenAI-compatible API (e.g. Groq, Google Gemini):
set `LLM_BASE_URL`, `LLM_API_KEY`, and `LLM_MODEL` according to the provider's documentation. Model names
and limits change, so check the current values with the provider.

Constants in the code that you can change:

- `knowledge.py`: `MASTERED` (mastery threshold, default 80), `CORE_TOPICS` (list of topics),
- `agent.py`: `MAX_STEPS` (limit of loop steps), `KEEP_MESSAGES` (how many of the most recent messages go
  to the model), and `SYSTEM` (the teacher prompt).

> The `CORE_TOPICS` list is loaded into the database only once, on first run. After changing it,
> delete `tutor.db` (while the app is stopped) so that the database is built anew. Deleting
> the file also erases all progress and added courses.

## Sandbox security

The student's code runs in a `python:3.12-slim` container with restrictions: no network
(`--network none`), 128 MB RAM, 0.5 CPU, a limit of 64 processes, a read-only file system (writing only in
`/tmp`), a non-root user, and a 5-second limit
per run. For this reason the student's code cannot install packages or download
data from the internet, and `input()` returns an error because the container has no input.

## Troubleshooting

| Symptom | Cause and solution |
|---|---|
| `File does not exist: app.py` or `No module named 'agent'` | the terminal is in the wrong folder: `cd` to the folder containing the files |
| `streamlit` is not recognized | run it via `python -m streamlit run app.py` |
| `ollama` / `docker` is not recognized | the program is not installed or the terminal was opened before installation: install it and open a new window |
| `failed to connect to the docker API` or the message "Docker is not running" | start Docker Desktop and wait for "Engine running" |
| Model connection error | Ollama is not running or the model is not downloaded: `ollama list`, and if it is missing, `ollama pull qwen2.5:14b` |
| Answers in a foreign language, "forgetting" the rules | context too short: check `ollama ps` during a conversation (CONTEXT should be 8192), set `OLLAMA_CONTEXT_LENGTH` and restart Ollama, then refresh the page |
| Raw JSON with `tool_call` appears in the chat | happens with local models: the app usually detects it on its own, and if not, click "New conversation" or try a different model |
| A rating does not appear in the dashboard | the model skipped saving it: tell it "save the rating" |
| Answers are slow | `ollama ps` should show `100% GPU`; with a GPU/CPU split the model or context is too large |

A quick check that the model is running on the GPU: in a second PowerShell window type `ollama ps`
during a conversation with the teacher.

## Limitations

- Rating is done by a local model, so it can be too lenient or too strict. The rating justifications are
  visible in the dashboard so that they can be verified.
- Paths are linear (topic order = dependency order), with no full dependency graph
  and no spaced repetition.
- Course import works by pasting the table of contents. The agent knows the section and lesson
  titles, but not their content.
- A topic's rating cannot be changed manually from the app.
- The Inter font is downloaded from Google Fonts. Without internet the app will use a system font.
