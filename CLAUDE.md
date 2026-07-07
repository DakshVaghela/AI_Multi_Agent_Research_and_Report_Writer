# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

An autonomous multi-agent research/report-writing system built on LangGraph. Given a topic, a graph of agents plans sub-questions, researches each one via web search, writes a structured report, and iteratively critiques/revises it before finalizing.

## Setup & commands

```bash
# Activate the existing venv (already created at .venv)
source .venv/bin/activate

# Install/update dependencies
python -m pip install -r requirements.txt

# Run all tests
pytest

# Run a single test file / test
pytest tests/test_workflow.py
pytest tests/test_workflow.py::test_workflow -v
```

Requirements to actually run the workflow end-to-end (not needed for pure unit tests that mock services):
- A local **Ollama** server reachable at `OLLAMA_BASE_URL` (default `http://localhost:11434`) serving the model named by `OLLAMA_MODEL` (default `llama3.2:3b`).
- A `TAVILY_API_KEY` in `.env` (required — `Settings` has no default and will fail to load without it).
- `.env` is loaded via `pydantic-settings` (`backend/config/settings.py`); see it for the full list of configurable env vars (`MONGO_URI`, `MONGO_DB`, `SQLITE_DB`, `MAX_SUB_QUESTIONS`, `MAX_REVISIONS`).

There is no app entrypoint yet — `frontend/`, `training/`, and `docker/` are placeholders (empty), and FastAPI/Streamlit are listed in `requirements.txt` but not wired up. The system is currently driven through tests (e.g. `tests/test_workflow.py`) that invoke the LangGraph workflow directly.

## Architecture

The core is a **LangGraph state machine** (`backend/graph/workflow.py`) over a single shared Pydantic state object, `ResearchState` (`backend/state/agent_state.py`): `topic`, `research_plan`, `research_notes`, `citations`, `draft_report`, `critique`, `revision_count`, `final_report`.

Graph shape: `START → planner → researcher → writer → critic → (writer | END)`. The `critic_router` (`backend/graph/router.py`) sends the state back to `writer` unless `state.final_report` has been set — the critic agent (not the router) decides when to stop, by either approving the report or hitting `MAX_REVISIONS`.

Each graph node (`backend/graph/nodes.py`) is a thin wrapper around a singleton agent instance from `backend/agents/`:
- **PlannerAgent** — turns the topic into a list of sub-questions (one per non-empty line of the LLM response).
- **ResearchAgent** — for each sub-question: searches, extracts article content from the top results, summarizes them into a `ResearchNote`, and accumulates `citations`. Iterates over *all* sub-questions in a single call.
- **WriterAgent** — turns accumulated research notes (+ any critic feedback) into a `Report` via a JSON-mode LLM call. Tolerates the LLM returning `main_content` as a dict of section→text (flattens it into markdown `## heading` sections) as well as a plain string.
- **CriticAgent** — reviews the draft report via a separate JSON-mode LLM call and produces a `Review` (approved flag + feedback text), written into `state.critique`.

Supporting service layer (`backend/services/`, `backend/search/`), all exposed as **module-level singletons** (e.g. `llm_service`, `search_service`, `content_extraction_service`, `summarization_service`, `report_service`) rather than injected dependencies:
- `llm_service` (`LazyLLMService`) — lazily constructs the real Ollama-backed `LLMService` on first use (avoids requiring Ollama/`ollama` package at import time). All agent LLM calls go through this one client; `json_mode=True` uses Ollama's grammar-constrained JSON decoding.
- `search_service` — fans a query out across multiple `BaseSearchProvider` implementations (`TavilyProvider`, `DDGSProvider`; `WikipediaProvider` also exists as a provider), merges results, and dedupes by URL. Provider failures are caught and logged per-provider, not fatal to the search as a whole.
- `content_extraction_service` — wraps `trafilatura` to pull clean article text from a URL.
- `summarization_service` — condenses extracted article text into a structured `Summary` (summary + key_points) via an LLM call; falls back to a raw-text `Summary` with empty `key_points` if JSON parsing fails.
- `report_service` — renders a final `Report` to PDF via `reportlab`.

**LLM output parsing**: every LLM call that expects structured data uses `json_mode=True` plus `backend/utils/json_parser.py`'s `parse_llm_json`, which strips markdown code fences and repairs truncated/malformed JSON (auto-closing open strings/brackets, backtracking from the parse error position) before falling back to raising. Agents build their JSON output payloads directly into the corresponding Pydantic model (`Report`, `Review`, `Summary`) via `Model(**data)` — when changing an LLM prompt's schema, keep it in sync with the matching model in `backend/models/` and the parsing/flattening logic in the agent.

Prompts live in `backend/prompts/` as one module-level string constant per agent (`PLANNER_SYSTEM_PROMPT`, `WRITER_SYSTEM_PROMPT`, `CRITIC_SYSTEM_PROMPT`, `SUMMARIZER_SYSTEM_PROMPT`) — these are the primary lever for changing agent behavior/output quality without touching code.
