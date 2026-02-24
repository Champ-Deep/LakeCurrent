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
    mode: Literal["auto", "filter", "glimpse"] | None = Query(
        default=None,
        description=(
            "Search engine selection. "
            "auto (default): LakeCurrent picks the best engine. "
            "filter: LakeFilter meta-search aggregation. "
            "glimpse: LakeGlimpse quick SERP lookup."
        ),
    ),
    categories: str | None = Query(None, description="Categories (LakeFilter only)"),
    language: str | None = Query(None, description="Language (LakeFilter only)"),
    pageno: int = Query(default=1, ge=1, le=100),
    limit: int = Query(default=settings.default_result_limit, ge=1, le=50),
):
    """LakeCurrent search — routes queries through available search engines."""
    effective_mode = mode or "auto"

    try:
        if effective_mode == "glimpse":
            response = await _lakeglimpse.search(q)
        else:
            # Both "auto" and "filter" route to LakeFilter for now.
            # "auto" is the future hook for smart routing and fallback logic.
            response = await _lakefilter.search(
                q, categories=categories, language=language, pageno=pageno
            )
    except (httpx.HTTPStatusError, httpx.TimeoutException, httpx.ConnectError):
        logger.exception("Search backend (%s) failed", effective_mode)
        return JSONResponse(
            status_code=503 if effective_mode == "glimpse" else 502,
            content={"detail": f"Search backend ({effective_mode}) is unavailable"},
        )
    except Exception:
        logger.exception("Unexpected error in search (%s)", effective_mode)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal search error"},
        )

    data = asdict(response)
    data["results"] = data["results"][:limit]
    return data
