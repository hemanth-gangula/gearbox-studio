"""
Gearbox Studio — FastAPI backend application.
"""
from __future__ import annotations

import os
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.services.design_service import PROJECTS_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("gearbox_studio")

app = FastAPI(
    title="Gearbox Studio API",
    description="Parametric Mechanical Gearbox Design & CAD Automation Platform",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS
# ALLOWED_ORIGINS env var: comma-separated list of frontend origins.
# Defaults to localhost for local dev.
# On Vercel set ALLOWED_ORIGINS=https://your-app.vercel.app
# ---------------------------------------------------------------------------
_raw = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000",
)
allowed_origins = [o.strip() for o in _raw.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.on_event("startup")
async def startup():
    os.makedirs(PROJECTS_DIR, exist_ok=True)
    logger.info("Gearbox Studio backend started")
    logger.info(f"Projects directory: {PROJECTS_DIR}")
    logger.info(f"CORS allowed origins: {allowed_origins}")


@app.get("/")
async def root():
    return {"service": "Gearbox Studio API", "docs": "/docs"}
