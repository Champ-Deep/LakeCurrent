import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.router import _lakefilter, _lakeglimpse, router

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await _lakefilter.close()
    await _lakeglimpse.close()


app = FastAPI(
    title="LakeCurrent",
    description="Comprehensive Search API for LakeB2B Agents",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(router)
