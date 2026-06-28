# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

"Lost and Found Logger" — a Streamlit web app that accepts one or more photos of physical "Found Article Forms", sends them concurrently to Gemini for vision-based extraction, and displays the structured results. The intended next step (not yet implemented) is writing results to Google Sheets.

## Running locally

Requires Python 3.14 and a `.env` file at the repo root:

```
GEMINI_API_KEY=<key>
GEMINI_MODEL=<model-name>
```

```bash
# Activate venv (bash)
source .venv/bin/activate
# Activate venv (PowerShell)
.venv\Scripts\Activate.ps1

streamlit run app.py
```

## Tests

```bash
pytest                              # all tests
pytest tests/services/test_ai_service.py   # single file
pytest -k test_returns_found_item   # single test by name
```

Dev dependencies (`requirements-dev.txt`): `pytest`, `pytest-mock`, `pytest-asyncio`.

Tests use dependency injection — `extract_found_item_data()` and `process_images_concurrently()` accept an optional `client` parameter, so tests pass a mock instead of hitting the real Gemini API. `conftest.py` sets a fake `GEMINI_API_KEY` env var before any imports to prevent the config module from raising on missing keys.

Both service functions are `async def`. Tests are written as `async def` coroutines and run via `pytest-asyncio` in `auto` mode (configured in `pytest.ini` — no `@pytest.mark.asyncio` decorator needed). The `mock_client` fixture in `conftest.py` sets `client.models.generate_content` to an `AsyncMock` so it can be awaited correctly.

## Docker

```bash
docker build -t smf-lnf .
docker run -p 8501:8501 --env-file .env smf-lnf
```

## Dev Container

A `.devcontainer/devcontainer.json` is configured for VSCode / GitHub Codespaces. It builds from the Dockerfile, forwards port 8501, installs the Python and Pylance extensions, and runs `pip install -r requirements-dev.txt` as a post-create command.

## Architecture

**Data flow**: `app.py` receives uploaded images (one or more) → opens each as a `PIL.Image` → calls `process_images_concurrently()` with `extract_found_item_data` as the processing function → images are dispatched to Gemini concurrently via a semaphore-bounded `asyncio.gather` (preserves input order) → each call returns a structured `FoundItem` (or `None` on failure) → results collected via `asyncio.run()` → converted to a DataFrame via `to_dataframe()` → offered as a CSV download button.

**Async client**: `ai_service.py` creates a module-level `async_client = genai.Client(api_key=GEMINI_API_KEY).aio` at import time. Both `extract_found_item_data` and `process_images_concurrently` are `async def` and accept this client as an injectable parameter (used by tests to pass a mock).

**Structured output**: The `FoundItem` Pydantic model (`src/models/llm_schemas.py`) is passed as `response_schema` to the Gemini API via `types.GenerateContentConfig`, which enforces JSON output matching the model's fields. Changing the schema changes what Gemini extracts.

**Config**: `src/core/config.py` loads env vars at import time. `GEMINI_API_KEY` is required — raises `ValueError` if missing. `GEMINI_MODEL` defaults to `"gemini-3.5-flash"` if not set, so it is optional in `.env`.

**Data export**: `data_service.to_dataframe()` (`src/services/data_service.py`) converts a `list[FoundItem | None]` to a pandas DataFrame (skipping `None` entries) with human-readable column headers; `app.py` serializes it via `df.to_csv(index=False)` and offers it as a download button.

## Key dependencies

`requirements.txt`: `streamlit`, `google-genai`, `pillow`, `python-dotenv`, `pydantic`, `pandas`

## Rules
* Don't use any commands that require permission from the user unless absolutely necessary.
* When making changes to the codebase, update CLAUDE.md to reflect those changes if they affect anything documented here (architecture, data flow, config, dependencies, commands, etc.). 
* You must follow the rules of Pylance's strict type checking