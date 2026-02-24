from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Literal

import httpx
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from app.clients.lakefilter import LakeFilterClient
from app.clients.lakeglimpse import LakeGlimpseClient
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

_lakefilter = LakeFilterClient(base_url=settings.lakefilter_base_url, timeout=settings.search_timeout)
_lakeglimpse = LakeGlimpseClient(base_url=settings.lakeglimpse_base_url, timeout=settings.search_timeout)


@router.get("/health")
async def health():
    checks = {
        "LakeFilter": await _lakefilter.is_healthy(),
        "LakeGlimpse": await _lakeglimpse.is_healthy(),
    }
    overall = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    status_code = 200 if overall == "healthy" else 503
    return JSONResponse(status_code=status_code, content={"status": overall, "components": checks})


@router.get("/search")
async def search(
    q: str = Query(..., min_length=1, max_length=500, description="The search query"),
    mode: Literal["filter", "glimpse", "current"] = Query(
        default="filter",
        description="Search mode: filter (LakeFilter), glimpse (LakeGlimpse), current (LakeCurrent)",
    ),
    categories: str | None = Query(None, description="Categories for LakeFilter"),
    language: str | None = Query(None, description="Language for LakeFilter"),
    pageno: int = Query(default=1, ge=1, le=100),
    limit: int = Query(default=settings.default_result_limit, ge=1, le=50),
):
    """LakeSource - The definitive starting point for all internal lookups."""
    try:
        if mode == "glimpse":
            response = await _lakeglimpse.search(q)
        elif mode == "current":
            return JSONResponse(
                status_code=501,
                content={"detail": "LakeCurrent integration is coming soon."},
            )
        else:
            response = await _lakefilter.search(
                q, categories=categories, language=language, pageno=pageno
            )
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError):
        logger.exception("Search backend (%s) failed", mode)
        return JSONResponse(
            status_code=503 if mode == "glimpse" else 502,
            content={"detail": f"Search backend ({mode}) is unavailable"},
        )
    except Exception:
        logger.exception("Unexpected error in search (%s)", mode)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal search error"},
        )

    data = asdict(response)
    data["results"] = data["results"][:limit]
    return data
