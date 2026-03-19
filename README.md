# LakeCurrent

**LakeCurrent** is a comprehensive search API built by **LakeB2B** as a self-hosted alternative to the Brave Search API. It provides a single, unified endpoint for web search — purpose-built for verification agents, qualification agents, sales agents, customer service agents, and scrapers.

## How It Works

LakeCurrent routes search queries through its internal engines and returns clean, structured JSON results.

| Engine | What It Does |
| :--- | :--- |
| **LakeFilter** | Meta-search aggregation. Returns ranked, deduplicated results with scores and metadata. |
| **LakeGlimpse** | Quick, privacy-focused SERP lookup without tracking. |

By default, LakeCurrent automatically selects the best engine for your query. You can also specify an engine explicitly via the `mode` parameter.

## Quick Start

1. Copy the environment file:
   ```bash
   cp .env.example .env
   ```

2. Launch with Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. Search:
   ```bash
   curl "http://localhost:8001/search?q=python+web+framework"
   ```

4. Interactive API docs: [http://localhost:8001/docs](http://localhost:8001/docs)

## API

### `GET /search`

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `q` | string | *required* | Search query (1–500 chars) |
| `mode` | string | `auto` | `auto`, `filter`, or `glimpse` |
| `categories` | string | — | Categories for LakeFilter (e.g. `news`, `images`) |
| `language` | string | — | Language for LakeFilter |
| `pageno` | int | `1` | Page number (1–100) |
| `limit` | int | `5` | Max results to return (1–50) |

**Example response:**
```json
{
  "query": "python web framework",
  "results": [
    {
      "url": "https://example.com",
      "title": "Example Result",
      "snippet": "A brief description of the result.",
      "engine": "google",
      "score": 3.5
    }
  ],
  "suggestions": [],
  "answers": [],
  "metadata": {
    "powered_by": "LakeB2B",
    "service": "LakeCurrent"
  }
}
```

### `GET /health`

Returns the status of all search engines.

```json
{
  "status": "healthy",
  "components": {
    "LakeFilter": "ok",
    "LakeGlimpse": "ok"
  }
}
```

## Architecture

```
┌──────────────────────────────────────────┐
│              LakeCurrent API             │
│            (FastAPI, Python 3.11+)       │
│                                          │
│   GET /search ──► auto / filter / glimpse│
│   GET /health                            │
└─────────┬───────────────┬────────────────┘
          │               │
    ┌─────▼─────┐   ┌────▼──────┐
    │ LakeFilter │   │LakeGlimpse│
    │            │   │           │
    └─────┬──────┘   └───────────┘
          │
    ┌─────▼─────┐
    │   Valkey   │
    │  (Cache)   │
    └────────────┘
```

All services run as Docker containers on a single bridge network.

## Development

```bash
cd backend
pip install -e ".[dev]"
pytest tests/ -v
```
