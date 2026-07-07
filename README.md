# AI Multi-Agent Research &amp; Report Writer

An autonomous, multi-agent research system that turns a single topic into a
structured, citation-backed report — and iteratively critiques and revises it
until it's good enough.

Given a topic, a **LangGraph** state machine coordinates four specialized LLM
agents that plan sub-questions, research each one via multi-provider web search,
write a structured report, and self-critique/revise it before finalizing. All
inference runs on a **local LLM via Ollama** (no paid API, fully private), and
the whole thing is exposed through a **FastAPI** backend with a **React +
TypeScript** frontend.

---

## Table of Contents

- [Architecture](#architecture)
- [How it works](#how-it-works)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend (local)](#backend-local)
  - [Frontend (local)](#frontend-local)
  - [Run with Docker](#run-with-docker)
- [Configuration](#configuration)
- [API reference](#api-reference)
- [Testing](#testing)
- [Engineering highlights](#engineering-highlights)

---

## Architecture

The core is a **LangGraph state machine** over a single shared Pydantic state
object (`ResearchState`). Four agents run as graph nodes, with the critic
driving a feedback loop back to the writer.

```
        ┌─────────┐     ┌────────────┐     ┌────────┐     ┌────────┐
START ─▶│ Planner │ ──▶ │ Researcher │ ──▶ │ Writer │ ──▶ │ Critic │
        └─────────┘     └────────────┘     └────────┘     └────────┘
                                               ▲               │
                                               │   revise      │  approved / max revisions
                                               └───────────────┤
                                                               ▼
                                                              END
```

- **Planner** — decomposes the topic into a list of research sub-questions.
- **Researcher** — for each sub-question: runs multi-provider web search,
  extracts article content from the top results **concurrently**, and
  summarizes them into a citation-backed research note.
- **Writer** — turns the accumulated research notes (plus any critic feedback)
  into a structured report, generated **section by section** for reliability.
- **Critic** — reviews the draft, and either approves it or sends it back to the
  writer with feedback. The loop stops on approval or when `MAX_REVISIONS` is hit.

The shared `ResearchState` carries: `topic`, `research_plan`, `research_notes`,
`citations`, `draft_report`, `critique`, `revision_count`, and `final_report`.

---

## How it works

1. **Plan** — the topic is expanded into sub-questions (one per line of the LLM
   response).
2. **Research** — each sub-question is searched across multiple providers
   (results merged and de-duplicated by URL); the top sources are fetched and
   cleaned with `trafilatura`, then summarized into a `ResearchNote` with
   `Citation`s.
3. **Write** — the writer assembles the report from focused, per-section LLM
   calls (title, executive summary, introduction, body sections, conclusion),
   with post-processing to strip hallucinated references and duplicate content.
4. **Critique &amp; revise** — the critic returns a structured `Review`
   (`approved` + `feedback`). If not approved, the writer revises using that
   feedback. This repeats until approval or `MAX_REVISIONS`.
5. **Export** — the final report is rendered to **PDF** via `reportlab`.

---

## Tech stack

| Layer | Technologies |
|-------|--------------|
| **Agents / Orchestration** | LangGraph, LangChain |
| **LLM inference** | Ollama (local, default `llama3.2:3b`), grammar-constrained JSON mode |
| **Web search** | Tavily, DuckDuckGo (`ddgs`), Wikipedia |
| **Content** | `trafilatura` (extraction), `reportlab` (PDF) |
| **Backend / API** | FastAPI, Uvicorn, Pydantic v2, `pydantic-settings` |
| **Data / Auth** | MongoDB (`pymongo`), PBKDF2-HMAC-SHA256 password hashing |
| **Frontend** | React 19, TypeScript, Vite, TailwindCSS, Framer Motion, React Router, Axios |
| **Infra** | Docker, Docker Compose |
| **Testing** | pytest |

---

## Project structure

```
backend/
  agents/        planner, researcher, writer, critic
  api/           FastAPI routers (auth, reports), background jobs, schemas
  config/        settings (pydantic-settings)
  graph/         LangGraph workflow, nodes, router
  models/        Pydantic models (Report, Review, Summary, Citation, ...)
  prompts/       one system-prompt module per agent
  search/        search service + providers (Tavily, DDGS, Wikipedia)
  services/      llm, content extraction, summarization, report (PDF), db
  state/         ResearchState (shared graph state)
  utils/         JSON repair parser, password hashing
  main.py        FastAPI app entrypoint
frontend/        React + TypeScript (Vite) single-page app
docker/          Dockerfile + container requirements
docker-compose.yml
tests/           pytest suite
```

---

## Getting started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for the frontend)
- **[Ollama](https://ollama.com)** running locally, with the model pulled:
  ```bash
  ollama pull llama3.2:3b
  ```
- **MongoDB** (local install, or use the Docker Compose stack below)
- A **[Tavily](https://tavily.com) API key** (required)

### Backend (local)

```bash
# 1. Create/activate a virtualenv
python -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
python -m pip install -r requirements.txt

# 3. Create a .env file (see Configuration below)

# 4. Run the API
uvicorn backend.main:app --reload --port 8000
```

The API is now at `http://localhost:8000` (health check: `GET /api/health`).

### Frontend (local)

```bash
cd frontend
npm install
npm run dev
```

The dev server runs at `http://localhost:5173` and proxies `/api` requests to
the backend at `http://localhost:8000` (configured in `vite.config.ts`).

### Run with Docker

The Compose stack runs the **API** and **MongoDB** in containers. Ollama stays
on the host (so it keeps GPU/Metal acceleration) and is reached via
`host.docker.internal`.

```bash
# Ensure Ollama is running on the host and .env is present, then:
docker compose up --build
```

- API: `http://localhost:8000`
- MongoDB: `localhost:27017` (persisted via a named volume)

---

## Configuration

Configuration is loaded from a `.env` file via `pydantic-settings`
(`backend/config/settings.py`).

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TAVILY_API_KEY` | **Yes** | — | Tavily web-search API key |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `llama3.2:3b` | Local model name |
| `MONGO_URI` | No | `mongodb://localhost:27017` | MongoDB connection string |
| `MONGO_DB` | No | `research_agent` | MongoDB database name |
| `MAX_SUB_QUESTIONS` | No | `5` | Max research sub-questions per topic |
| `MAX_REVISIONS` | No | `3` | Max writer↔critic revision loops |

Example `.env`:

```env
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxx
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
MONGO_URI=mongodb://localhost:27017
```

---

## API reference

Base path: `/api`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | Health check |
| `POST` | `/auth/signup` | Register a user (`email`, `password`, optional `name`) |
| `POST` | `/auth/login` | Authenticate a user |
| `POST` | `/reports` | Start a report job for a `topic` — returns a `job_id` (202) |
| `GET`  | `/reports/{job_id}` | Poll job status (`pending` / `running` / `completed` / `failed`) |
| `GET`  | `/reports/{job_id}/pdf` | Download the finished report as PDF |

Report generation runs as an **asynchronous background job**: `POST /reports`
returns immediately with a `job_id`, and the client polls
`GET /reports/{job_id}` until the report is ready.

---

## Testing

```bash
pytest                       # run the full suite
pytest tests/test_workflow.py -v
```

---

## Engineering highlights

- **Multi-agent orchestration** with a LangGraph state machine and a
  self-correcting critic→writer feedback loop bounded by a max-revision guard.
- **Local, cost-free LLM inference** via Ollama, with per-call generation
  parameters (temperature, context window, output length) tuned per agent step.
- **Prompt engineering for small models** — report generation is decomposed into
  focused per-section calls, because a single large JSON call caused the model
  to ignore length constraints and exploit grammar-constrained decoding by
  returning empty strings.
- **LLM output-reliability layer** — strips fabricated references, de-duplicates
  padded paragraphs, retries empty generations, and caps per-note source text to
  avoid silent context-window overflow.
- **Structured output** via JSON mode + Pydantic validation, backed by a custom
  fault-tolerant JSON parser that repairs truncated/malformed responses.
- **Concurrency** — independent source fetches are extracted in parallel with a
  thread pool, collapsing N sequential round-trips to the slowest single fetch.
- **Production-style backend** — FastAPI with async job queue, MongoDB auth
  (PBKDF2-SHA256 hashing), and full Docker Compose containerization.
