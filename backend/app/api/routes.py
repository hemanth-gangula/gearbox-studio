"""
FastAPI route handlers for the Gearbox Studio backend.
"""
from __future__ import annotations

import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse, PlainTextResponse, JSONResponse

from app.schemas.design import (
    GearboxDesign,
    CalculationResults,
    ValidationResult,
    BOM,
    DrawingInfo,
    DesignRecord,
    DesignSummary,
    HealthResponse,
    JobInfo,
)
from app.services import design_service
from app.calculations.gear_calcs import calculate_design
from app.validation.validator import validate_design

router = APIRouter(prefix="/api")


@router.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        cad_engine="ezdxf + trimesh (custom STEP exporter)",
        available_formats=design_service.get_available_formats(),
    )


@router.post("/designs/validate", response_model=ValidationResult)
async def validate(design: GearboxDesign):
    """Validate a design configuration without generating files."""
    calc = calculate_design(design)
    return validate_design(design, calc)


@router.post("/designs/calculate", response_model=CalculationResults)
async def calculate(design: GearboxDesign):
    """Calculate engineering dimensions for a design."""
    return calculate_design(design)


@router.post("/designs/generate")
async def generate(design: GearboxDesign):
    """Create a new design and start generation. Returns design_id and job_id."""
    design_id = design_service.save_design(design)
    job_id = design_service.start_generation(design_id)
    return {"design_id": design_id, "job_id": job_id}


@router.get("/jobs/{job_id}", response_model=JobInfo)
async def get_job(job_id: str):
    """Get the status of a generation job."""
    job = design_service.job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/designs", response_model=list[DesignSummary])
async def list_designs():
    """List all saved designs."""
    return design_service.list_designs()


@router.get("/designs/{design_id}", response_model=DesignRecord)
async def get_design(design_id: str):
    """Get a specific design record."""
    record = design_service.get_design(design_id)
    if not record:
        raise HTTPException(status_code=404, detail="Design not found")
    return record


@router.get("/designs/{design_id}/drawings", response_model=list[DrawingInfo])
async def get_drawings(design_id: str):
    """Get the list of drawings for a design."""
    drawings = design_service.get_drawings(design_id)
    if drawings is None:
        raise HTTPException(status_code=404, detail="Design not found or not generated")
    return drawings


@router.get("/designs/{design_id}/components")
async def get_components(design_id: str):
    """Get the component list for a design."""
    components = design_service.get_components(design_id)
    if components is None:
        raise HTTPException(status_code=404, detail="Design not found or not generated")
    return components


@router.get("/designs/{design_id}/bom", response_model=BOM)
async def get_bom(design_id: str):
    """Get the Bill of Materials for a design."""
    bom = design_service.get_bom(design_id)
    if bom is None:
        raise HTTPException(status_code=404, detail="Design not found or not generated")
    return bom


@router.get("/designs/{design_id}/validation", response_model=ValidationResult)
async def get_validation(design_id: str):
    """Get validation results for a design."""
    validation = design_service.get_validation(design_id)
    if validation is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return validation


@router.get("/designs/{design_id}/calculations", response_model=CalculationResults)
async def get_calculations(design_id: str):
    """Get calculation results for a design."""
    calc = design_service.get_calculations(design_id)
    if calc is None:
        raise HTTPException(status_code=404, detail="Design not found")
    return calc


@router.get("/designs/{design_id}/file/{filename}")
async def download_file(design_id: str, filename: str):
    """Download a specific file for a design."""
    filepath = design_service.get_file_path(design_id, filename)
    if not filepath:
        raise HTTPException(status_code=404, detail="File not found or not available")
    return FileResponse(filepath, filename=filename)


@router.get("/designs/{design_id}/files")
async def list_files(design_id: str):
    """List all available files for a design."""
    record = design_service.get_design(design_id)
    if not record:
        raise HTTPException(status_code=404, detail="Design not found")
    files_info = {}
    for fmt, fname in record.files.items():
        filepath = design_service.get_file_path(design_id, fname)
        if filepath and os.path.isfile(filepath):
            size = os.path.getsize(filepath)
            files_info[fmt] = {
                "filename": fname,
                "size_bytes": size,
                "available": True,
            }
        else:
            files_info[fmt] = {
                "filename": fname,
                "available": False,
            }
    return {"design_id": design_id, "files": files_info}
