# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project does

"Lost and Found Logger" — a Streamlit web app that accepts a photo of a physical "Found Article Form", sends it to Gemini for vision-based extraction, and displays the structured results. The intended next step (not yet implemented) is writing results to Google Sheets.

## Running locally

Requires Python 3.14 and a `.env` file at the repo root with `GEMINI_API_KEY=<key>`.

```bash
# Activate the virtual environment
source .venv/bin/activate

# Run the app
streamlit run app.py
```

App is served at `http://localhost:8501`.

## Docker

```bash
docker build -t smf-lnf .
docker run -p 8501:8501 --env-file .env smf-lnf
```

## Architecture

```
app.py                      # Streamlit UI entry point
src/
  core/config.py            # Loads GEMINI_API_KEY from .env; raises on missing key
  models/llm_schemas.py     # Pydantic model (FoundItem) — defines the structured output schema sent to Gemini
  services/ai_service.py    # Gemini client; extract_found_item_data() takes an image path, returns a FoundItem
```

**Data flow**: `app.py` receives an uploaded image → writes it to a temp file → calls `extract_found_item_data(path)` in `ai_service.py` → Gemini `gemini-2.0-flash` returns structured JSON constrained by the `FoundItem` schema → result displayed in the UI.

**Structured output**: The `FoundItem` Pydantic model is passed directly as `response_schema` to the Gemini API (`types.GenerateContentConfig`), which enforces JSON output matching the model's fields. Changing the schema in `llm_schemas.py` changes what Gemini extracts.

## Key dependencies

| Package | Version | Purpose |
|---|---|---|
| `streamlit` | 1.58.0 | UI |
| `google-genai` | 2.8.0 | Gemini API client |
| `pillow` | 12.2.0 | Image loading |
| `python-dotenv` | 1.2.2 | `.env` loading |


## Rules
* Don't use any commands that require permission from the user unless absolutely neccessary. 