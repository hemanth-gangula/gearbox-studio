# Architecture

## Overview

Gearbox Studio is a full-stack web application for parametric mechanical gearbox design and CAD automation. It consists of a Python FastAPI backend that performs engineering calculations and generates CAD files, and a Next.js/React frontend that provides a professional engineering UI with an interactive 3D viewer.

## System Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Frontend (Next.js)                  │
│  React + TypeScript + Tailwind CSS + React Three Fiber │
│  Port 3000                                            │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP/REST (JSON + file downloads)
┌──────────────────────┴──────────────────────────────┐
│                   Backend (FastAPI)                    │
│  Python + Pydantic + NumPy                             │
│  Port 8000                                             │
│                                                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │
│  │ Calculations │ │  CAD Engine  │ │  Exporters   │   │
│  │ (gear_calcs) │ │ (DXF + Mesh  │ │ (BOM, Report,│   │
│  │              │ │  + STEP)     │ │  Package)    │   │
│  └──────────────┘ └──────────────┘ └──────────────┘   │
│  ┌──────────────┐ ┌──────────────┐                     │
│  │ Validation   │ │ Job Manager  │                     │
│  └──────────────┘ └──────────────┘                     │
└──────────────────────┬──────────────────────────────┘
                       │
                ┌──────┴──────┐
                │  projects/  │  (generated files)
                │  {design_id}│
                └─────────────┘
```

## Backend Components

### Calculations (`app/calculations/gear_calcs.py`)
- Pitch diameter: d = m × z
- Centre distance: a = (d1 + d2) / 2
- Reduction ratio: i = z2 / z1
- Output speed: n2 = n1 / i
- Base circle: db = d × cos(α)
- Addendum: ha = m (standard)
- Dedendum: hf = 1.25 × m (standard + clearance)

### CAD Engine
- **DXF Generation** (`app/cad/dxf_generator.py`): Uses ezdxf to generate 9 engineering drawing sheets with organized CAD layers (OUTLINE, HIDDEN, CENTER, DIMENSIONS, etc.)
- **3D Mesh Generation** (`app/cad/mesh_generator.py`): Uses trimesh to create parametric 3D meshes for all gearbox components (gears with simplified involute teeth, stepped shafts, housing, bearings, keys, fasteners)
- **STEP Export** (`app/cad/step_exporter.py`): Custom STEP (ISO 10303-21 AP214) generator producing faceted B-rep solids (cylinders as n-sided prisms, rectangular boxes) without requiring OpenCASCADE

### Exporters
- BOM CSV/XLSX (openpyxl)
- Engineering Report PDF (reportlab) + Markdown
- AutoCAD Script (.scr) + AutoLISP (.lsp)
- ZIP package

### Job Manager (`app/jobs/job_manager.py`)
Thread-safe in-memory store tracking generation progress through stages: validating → calculating → generating_components → generating_drawings → building_assembly → exporting_previews → creating_bom → generating_reports → running_validation → completed

## Frontend Components

### Layout
- Sidebar with 11 navigation sections
- TopBar with project name, save status, theme toggle
- DesignProvider context for state management

### 3D Viewer
- React Three Fiber + @react-three/drei
- Loads GLB file from backend
- OrbitControls for rotate, zoom, pan
- Wireframe toggle
- Explode factor slider

### Pages
1. Dashboard — project overview, validation status, export availability
2. New Design — comprehensive parameter form with validation
3. Design Parameters — calculation results with formulas
4. 2D Drawings — list of 9 DXF sheets with download
5. 3D Model — interactive viewer with component tree
6. Assembly Explorer — 3D viewer with detailed component info
7. Exploded View — explosion distance slider with parts list
8. Bill of Materials — sortable BOM table with CSV/XLSX export
9. Engineering Reports — report preview with PDF/MD download
10. Export Center — all file formats with download buttons
11. Settings — theme, backend status, environment info

## Data Flow

1. User enters parameters in the New Design form
2. Frontend sends POST /api/designs/generate with full GearboxDesign config
3. Backend saves design, creates a job, starts generation thread
4. Generation pipeline:
   a. Validates parameters
   b. Calculates gear dimensions
   c. Generates 3D meshes → GLB
   d. Generates STEP file
   e. Generates 9 DXF drawings
   f. Creates BOM (CSV + XLSX)
   g. Generates report (PDF + Markdown)
   h. Creates AutoCAD scripts
   i. Packages everything into ZIP
5. Frontend polls job status and updates UI
6. User can browse drawings, 3D model, BOM, reports, and download files

## Key Design Decisions

- **No database**: Uses in-memory storage for jobs and design records. Sufficient for single-user local development.
- **No authentication**: Local development tool, not a multi-user service.
- **Custom STEP exporter**: Python 3.14 doesn't have pre-built OpenCASCADE wheels, so a custom faceted STEP generator was implemented.
- **trimesh for 3D**: Creates real parametric geometry (not just placeholder boxes) with simplified involute gear teeth.
- **Background generation**: DXF and mesh generation can take several seconds, so it runs in a background thread with progress polling.
