"""
Gearbox Studio — FastAPI backend application.

Provides engineering calculation, DXF drawing generation, 3D mesh generation,
STEP export, BOM, report generation, and design management APIs.
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

# CORS — allow the frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"],
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


@app.get("/")
async def root():
    return {"service": "Gearbox Studio API", "docs": "/docs"}
