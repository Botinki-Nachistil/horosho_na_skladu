from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import close_db, init_db
from exceptions import http_exception_handler
from routers.tasks import router as tasks_router
from routers.waves import router as waves_router
from routers.optimizer import router as optimizer_router
from routers.mobile import router as mobile_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    await close_db()


app = FastAPI(
    title="Warehouse Operations API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

app.add_exception_handler(HTTPException, http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"

app.include_router(tasks_router, prefix=API_PREFIX)
app.include_router(waves_router, prefix=API_PREFIX)
app.include_router(optimizer_router, prefix=API_PREFIX)
app.include_router(mobile_router, prefix=API_PREFIX)


@app.get("/healthz", tags=["health"])
async def healthcheck():
    return {"status": "ok"}
