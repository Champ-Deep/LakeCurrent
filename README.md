# LakeCurrent

**LakeCurrent** is the search and intelligence hub for the **LakeB2B** Data Reservoir series. It provides a unified interface for deep, private, and real-time data lookups, ensuring a clean and modern flow of information.

## The Data Reservoir Nomenclature

In alignment with the LakeB2B ecosystem, this project uses a water-themed naming convention for its core components:

| Component | Role |
| :--- | :--- |
| **LakeSource** | The definitive starting point for all internal search queries (FastAPI Router). |
| **LakeFilter** | Aggregates and cleans results from multiple data streams to ensure purity. |
| **LakeGlimpse** | A quick, private glimpse into search results via a privacy-focused reflection. |
| **LakeCurrent** | The fast, modern flow of real-time search data (namesake of the project). |

---

## Architecture

- **Backend**: FastAPI (Python 3.11+)
- **Components**:
    - LakeFilter (meta-search aggregation)
    - LakeGlimpse (private search reflection)
    - LakeCurrent (real-time search API)
- **Deployment**: Docker Compose

## Getting Started

1. **Environment Setup**:
   Copy `.env.example` to `.env` and fill in your API keys.

2. **Launch**:
   ```bash
   docker-compose up -d
   ```

3. **API Access**:
   The API will be available at `http://localhost:8001/docs`.

## API Endpoints

| Endpoint | Description |
| :--- | :--- |
| `GET /search?q=...&mode=filter` | Search via LakeFilter (default mode) |
| `GET /search?q=...&mode=glimpse` | Search via LakeGlimpse |
| `GET /search?q=...&mode=current` | Search via LakeCurrent (coming soon) |
| `GET /health` | Health check for all components |
