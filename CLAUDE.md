# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

"Lost and Found Logger" — a Streamlit web app that accepts a photo of a physical "Found Article Form", sends it to Gemini for vision-based extraction, and displays the structured results. The intended next step (not yet implemented) is writing results to Google Sheets.

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

Dev dependencies (`requirements-dev.txt`): `pytest`, `pytest-mock`.

Tests use dependency injection — `extract_found_item_data()` accepts an optional `client` parameter, so tests pass a `MagicMock` instead of hitting the real Gemini API. `conftest.py` sets a fake `GEMINI_API_KEY` env var before any imports to prevent the config module from raising on missing keys.

## Docker

```bash
docker build -t smf-lnf .
docker run -p 8501:8501 --env-file .env smf-lnf
```

## Architecture

**Data flow**: `app.py` receives an uploaded image → opens it as a `PIL.Image` → calls `extract_found_item_data(image)` in `ai_service.py` → Gemini returns structured JSON constrained by the `FoundItem` schema → result displayed in the UI.

**Structured output**: The `FoundItem` Pydantic model (`src/models/llm_schemas.py`) is passed as `response_schema` to the Gemini API via `types.GenerateContentConfig`, which enforces JSON output matching the model's fields. Changing the schema changes what Gemini extracts.

**Config**: `src/core/config.py` loads `GEMINI_API_KEY` and `GEMINI_MODEL` from `.env` at import time and raises if either is missing. The model name is not hardcoded — it comes from the environment.

## Key dependencies

`requirements.txt`: `streamlit`, `google-genai`, `pillow`, `python-dotenv`

## Rules
* Don't use any commands that require permission from the user unless absolutely necessary.
* When making changes to the codebase, update CLAUDE.md to reflect those changes if they affect anything documented here (architecture, data flow, config, dependencies, commands, etc.). 