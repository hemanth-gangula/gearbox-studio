"""
Design service — orchestrates the full design generation workflow.

Ties together validation, calculations, DXF generation, 3D mesh generation,
STEP export, BOM creation, report generation, and packaging.
Runs as a background task with progress tracking via the job manager.
"""
from __future__ import annotations

import os
import threading
import uuid
import json
import math
from datetime import datetime
from typing import Optional

from app.schemas.design import (
    GearboxDesign,
    CalculationResults,
    ValidationResult,
    ValidationIssue,
    BOM,
    ComponentInfo,
    DrawingInfo,
    DesignRecord,
    DesignSummary,
    JobStatus,
    JobStage,
)
from app.calculations.gear_calcs import calculate_design
from app.validation.validator import validate_design
from app.cad.dxf_generator import generate_all_drawings
from app.cad.mesh_generator import generate_all_meshes, get_component_info_list, MeshComponent
from app.cad.step_exporter import generate_step_file
from app.exporters.bom_exporter import build_bom, export_bom_csv, export_bom_xlsx
from app.exporters.report_generator import generate_markdown_report, generate_pdf_report
from app.exporters.package_exporter import (
    create_zip_package,
    generate_autocad_script,
    generate_autolisp_file,
)
from app.jobs.job_manager import job_manager


# Global store for design records (in-memory, thread-safe)
_designs: dict[str, DesignRecord] = {}
_designs_lock = threading.Lock()

# Base directory for project files
PROJECTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "projects")


def _ensure_project_dir(design_id: str) -> str:
    """Create and return the output directory for a design."""
    d = os.path.join(PROJECTS_DIR, design_id)
    os.makedirs(d, exist_ok=True)
    return d


def save_design(design: GearboxDesign) -> str:
    """Save a design configuration and return its ID."""
    design_id = str(uuid.uuid4())[:8]
    record = DesignRecord(
        design_id=design_id,
        project_name=design.project_info.project_name,
        drawing_number=design.project_info.drawing_number,
        created_at=datetime.now().isoformat(),
        config=design,
    )
    with _designs_lock:
        _designs[design_id] = record
    return design_id


def get_design(design_id: str) -> Optional[DesignRecord]:
    with _designs_lock:
        return _designs.get(design_id)


def list_designs() -> list[DesignSummary]:
    with _designs_lock:
        summaries = []
        for record in _designs.values():
            calc = record.calculations
            summaries.append(DesignSummary(
                design_id=record.design_id,
                project_name=record.project_name,
                drawing_number=record.drawing_number,
                created_at=record.created_at,
                reduction_ratio=calc.reduction_ratio if calc else 0,
                module=record.config.gear_parameters.module,
                input_teeth=record.config.gear_parameters.input_teeth,
                output_teeth=record.config.gear_parameters.output_teeth,
                centre_distance=calc.centre_distance if calc else 0,
                input_pitch_diameter=calc.input_pitch_diameter if calc else 0,
                output_pitch_diameter=calc.output_pitch_diameter if calc else 0,
                status="generated" if record.files else "configured",
                files=record.files,
            ))
        return summaries


def run_generation(design_id: str, job_id: str):
    """
    Run the full design generation pipeline in a background thread.
    This function is designed to be called via threading.Thread.
    """
    try:
        record = get_design(design_id)
        if not record:
            job_manager.update_job(job_id, status=JobStatus.FAILED, stage=JobStage.FAILED,
                                    error="Design not found", progress=0)
            return

        design = record.config
        output_dir = _ensure_project_dir(design_id)
        files = {}

        # Stage 1: Validating
        job_manager.update_job(job_id, stage=JobStage.VALIDATING, progress=5,
                                message="Validating parameters...")
        validation = validate_design(design)
        record.validation = validation
        if not validation.is_valid:
            errors = [i.message for i in validation.issues if i.severity == "error"]
            job_manager.update_job(job_id, status=JobStatus.FAILED, stage=JobStage.FAILED,
                                    error="; ".join(errors[:3]), progress=0)
            return

        # Stage 2: Calculating
        job_manager.update_job(job_id, stage=JobStage.CALCULATING, progress=15,
                                message="Calculating dimensions...")
        calc = calculate_design(design)
        record.calculations = calc

        # Stage 3: Generating components (3D meshes)
        job_manager.update_job(job_id, stage=JobStage.GENERATING_COMPONENTS, progress=25,
                                message="Generating 3D component meshes...")
        components, glb_path = generate_all_meshes(design, calc, output_dir)
        if os.path.isfile(glb_path):
            files["glb"] = os.path.basename(glb_path)
            record.files["glb"] = os.path.basename(glb_path)

        # STEP export
        try:
            step_path = os.path.join(output_dir, "gearbox_assembly.stp")
            generate_step_file(components, step_path, "gearbox_assembly.stp")
            if os.path.isfile(step_path):
                files["step"] = "gearbox_assembly.stp"
                record.files["step"] = "gearbox_assembly.stp"
        except Exception as e:
            # STEP is best-effort
            pass

        # Stage 4: Generating 2D drawings (DXF)
        job_manager.update_job(job_id, stage=JobStage.GENERATING_DRAWINGS, progress=40,
                                message="Generating 2D DXF drawings...")
        drawings = generate_all_drawings(design, calc, output_dir)
        for d in drawings:
            filepath = os.path.join(output_dir, d.filename)
            if os.path.isfile(filepath):
                files[f"dxf_{d.drawing_id}"] = d.filename

        # Stage 5: Building assembly
        job_manager.update_job(job_id, stage=JobStage.BUILDING_ASSEMBLY, progress=55,
                                message="Building assembly...")

        # Stage 6: Exporting previews (already done with GLB)
        job_manager.update_job(job_id, stage=JobStage.EXPORTING_PREVIEWS, progress=65,
                                message="Exporting previews...")

        # Stage 7: Creating BOM
        job_manager.update_job(job_id, stage=JobStage.CREATING_BOM, progress=75,
                                message="Creating BOM...")
        comp_infos = get_component_info_list(components)
        bom = build_bom(comp_infos)
        record.bom = bom

        bom_csv_path = os.path.join(output_dir, "bom.csv")
        export_bom_csv(bom, bom_csv_path)
        if os.path.isfile(bom_csv_path):
            files["bom_csv"] = "bom.csv"

        bom_xlsx_path = os.path.join(output_dir, "bom.xlsx")
        export_bom_xlsx(bom, bom_xlsx_path)
        if os.path.isfile(bom_xlsx_path):
            files["bom_xlsx"] = "bom.xlsx"

        # Stage 8: Generating reports
        job_manager.update_job(job_id, stage=JobStage.GENERATING_REPORTS, progress=85,
                                message="Generating reports...")
        md_path = os.path.join(output_dir, "report.md")
        generate_markdown_report(design, calc, validation, bom, drawings, md_path)
        if os.path.isfile(md_path):
            files["report_md"] = "report.md"

        pdf_path = os.path.join(output_dir, "report.pdf")
        generate_pdf_report(design, calc, validation, bom, drawings, pdf_path)
        if os.path.isfile(pdf_path):
            files["report_pdf"] = "report.pdf"

        # AutoCAD scripts
        scr_path = os.path.join(output_dir, "gearbox.scr")
        generate_autocad_script(design, calc, scr_path)
        if os.path.isfile(scr_path):
            files["autocad_scr"] = "gearbox.scr"

        lsp_path = os.path.join(output_dir, "gearbox.lsp")
        generate_autolisp_file(design, calc, lsp_path)
        if os.path.isfile(lsp_path):
            files["autolisp"] = "gearbox.lsp"

        # Stage 9: Running validation
        job_manager.update_job(job_id, stage=JobStage.RUNNING_VALIDATION, progress=90,
                                message="Running validation...")

        # Update design record with files
        record.files = files

        # Save design record to disk as JSON
        record_path = os.path.join(output_dir, "design_record.json")
        with open(record_path, "w") as f:
            json.dump({
                "design_id": record.design_id,
                "project_name": record.project_name,
                "drawing_number": record.drawing_number,
                "created_at": record.created_at,
                "config": record.config.model_dump(),
                "calculations": record.calculations.model_dump() if record.calculations else None,
                "validation": record.validation.model_dump() if record.validation else None,
                "bom": record.bom.model_dump() if record.bom else None,
                "files": files,
            }, f, indent=2, default=str)

        # Create ZIP package
        zip_files = {}
        for fmt, fname in files.items():
            zip_files[fname] = os.path.join(output_dir, fname)
        zip_path = os.path.join(output_dir, "gearbox_studio_package.zip")
        create_zip_package(zip_files, zip_path)
        if os.path.isfile(zip_path):
            files["zip"] = "gearbox_studio_package.zip"
            record.files["zip"] = "gearbox_studio_package.zip"

        # Completed
        job_manager.update_job(job_id, status=JobStatus.COMPLETED, stage=JobStage.COMPLETED,
                                progress=100, message="Generation completed successfully",
                                files=files)

    except Exception as e:
        job_manager.update_job(job_id, status=JobStatus.FAILED, stage=JobStage.FAILED,
                                error=str(e), progress=0)


def start_generation(design_id: str) -> str:
    """Start a background generation job and return the job ID."""
    job = job_manager.create_job(design_id)
    thread = threading.Thread(target=run_generation, args=(design_id, job.job_id), daemon=True)
    thread.start()
    return job.job_id


def get_drawings(design_id: str) -> Optional[list[DrawingInfo]]:
    """Return the list of drawings for a design."""
    record = get_design(design_id)
    if not record or not record.calculations:
        return None
    output_dir = os.path.join(PROJECTS_DIR, design_id)
    drawings = []
    drawing_specs = [
        ("01_general_assembly", "General Assembly", "Front, top, side, and isometric reference views."),
        ("02_gearbox_housing", "Gearbox Housing", "Housing views with internal cavity and mounting holes."),
        ("03_input_shaft", "Input Shaft", "Stepped input shaft with bearing seats and keyway."),
        ("04_output_shaft", "Output Shaft", "Stepped output shaft with bearing seats and keyway."),
        ("05_input_gear", "Input Gear", "Input pinion gear views with pitch circle and tooth parameters."),
        ("06_output_gear", "Output Gear", "Output gear views with pitch circle and tooth parameters."),
        ("07_housing_cover", "Housing Cover", "Cover plan and elevation views with fastener holes."),
        ("08_assembly_section", "Assembly Section", "Sectional view of internal gear arrangement."),
        ("09_exploded_assembly", "Exploded Assembly", "Exploded view with numbered callouts and parts list."),
    ]
    for file_base, name, desc in drawing_specs:
        filename = f"{file_base}.dxf"
        dxf_available = os.path.isfile(os.path.join(output_dir, filename))
        drawings.append(DrawingInfo(
            drawing_id=file_base, name=name, description=desc,
            filename=filename, dxf_available=dxf_available,
        ))
    return drawings


def get_components(design_id: str) -> Optional[list[ComponentInfo]]:
    """Return component info for a design."""
    record = get_design(design_id)
    if not record or not record.bom:
        return None
    return record.bom.components


def get_bom(design_id: str) -> Optional[BOM]:
    record = get_design(design_id)
    if not record or not record.bom:
        return None
    return record.bom


def get_validation(design_id: str) -> Optional[ValidationResult]:
    record = get_design(design_id)
    if not record or not record.validation:
        # Run validation on the fly if not yet done
        if record:
            calc = calculate_design(record.config)
            validation = validate_design(record.config, calc)
            record.validation = validation
            return validation
        return None
    return record.validation


def get_calculations(design_id: str) -> Optional[CalculationResults]:
    record = get_design(design_id)
    if not record:
        return None
    if not record.calculations:
        calc = calculate_design(record.config)
        record.calculations = calc
        return calc
    return record.calculations


def get_file_path(design_id: str, filename: str) -> Optional[str]:
    """Get the absolute path for a file, with path traversal protection."""
    # Prevent path traversal
    safe_name = os.path.basename(filename)
    if safe_name != filename:
        return None
    output_dir = os.path.join(PROJECTS_DIR, design_id)
    filepath = os.path.join(output_dir, safe_name)
    if os.path.isfile(filepath):
        return filepath
    return None


def get_available_formats() -> list[str]:
    """Return the list of available export formats."""
    return [
        "DXF (2D drawings)",
        "GLB (3D preview)",
        "STEP (3D geometry — faceted approximation)",
        "STL (3D mesh — per component)",
        "CSV (BOM)",
        "XLSX (BOM)",
        "PDF (engineering report)",
        "Markdown (engineering report)",
        "SCR (AutoCAD script)",
        "LSP (AutoLISP)",
        "ZIP (complete package)",
    ]
