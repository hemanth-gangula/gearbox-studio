# Gearbox Studio

**Parametric Mechanical Gearbox Design & CAD Automation Platform**

Gearbox Studio is a full-stack web application for designing single-stage spur gear reduction units. It performs engineering calculations, generates editable DXF drawings, creates 3D models, produces a Bill of Materials, generates engineering reports, and exports CAD files in multiple formats.

## Features

- **Parametric Design**: Configure gear, shaft, housing, and assembly parameters
- **Engineering Calculations**: Pitch diameter, centre distance, reduction ratio, base circle, output speed
- **2D CAD Drawings**: 9 editable DXF sheets with organized layers and title blocks
- **3D Model Generation**: Parametric meshes with simplified involute gear teeth
- **Interactive 3D Viewer**: React Three Fiber with orbit controls, wireframe mode, and component tree
- **Exploded Assembly**: Interactive explosion distance slider with parts list
- **Bill of Materials**: Sortable BOM table with CSV and XLSX export
- **Engineering Reports**: PDF and Markdown reports with calculations, validation, and BOM
- **Export Center**: DXF, GLB, STEP, STL, CSV, XLSX, PDF, Markdown, AutoCAD scripts, ZIP package
- **Validation Engine**: Engineering checks for gear, shaft, housing, and assembly compatibility

## Quick Start

### Prerequisites

- Python 3.14+
- Node.js 22+

### Setup

```powershell
# Install all dependencies
.\scripts\setup.ps1

# Start both services
.\scripts\start.ps1
```

### Manual Start

**Backend** (terminal 1):
```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Frontend** (terminal 2):
```powershell
cd frontend
npm install
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API docs**: http://127.0.0.1:8000/docs

## How to Generate a Gearbox Design

1. Open http://localhost:3000
2. Click **New Design** in the sidebar
3. Configure parameters (or use defaults):
   - Gear type: Spur External
   - Input teeth: 20, Output teeth: 60
   - Module: 2 mm, Pressure angle: 20°
4. Click **Validate** to check the design
5. Click **Generate Design** to create all outputs
6. Wait for generation to complete (progress shown in top bar)
7. Navigate through the sidebar to view:
   - **Design Parameters**: Calculation results with formulas
   - **2D Drawings**: 9 DXF sheets, downloadable
   - **3D Model**: Interactive viewer with component tree
   - **Assembly Explorer**: Component details
   - **Exploded View**: Explosion slider with parts list
   - **Bill of Materials**: BOM table with CSV/XLSX download
   - **Engineering Reports**: PDF and Markdown
   - **Export Center**: All files available for download

## How to Download Files

1. Navigate to **Export Center**
2. Browse available files by category:
   - 2D Drawings (DXF): 9 sheets
   - 3D Models: GLB preview, STEP geometry
   - Bill of Materials: CSV, XLSX
   - Engineering Reports: PDF, Markdown
   - AutoCAD Scripts: .scr, .lsp
   - Complete Package: ZIP
3. Click **Download** for any available file

## Supported Export Formats

| Format | Description | Engine |
|--------|-------------|--------|
| DXF | Editable 2D CAD drawings | ezdxf |
| GLB | 3D assembly preview (browser) | trimesh |
| STEP | 3D geometry exchange | Custom exporter (faceted) |
| STL | 3D mesh per component | trimesh |
| CSV | Bill of Materials | Python stdlib |
| XLSX | Bill of Materials (Excel) | openpyxl |
| PDF | Engineering report | reportlab |
| Markdown | Engineering report | Python stdlib |
| SCR | AutoCAD script | Custom generator |
| LSP | AutoLISP routine | Custom generator |
| ZIP | Complete package | Python stdlib |
| DWG | Native AutoCAD | **Not available** (requires AutoCAD) |

## Technology Stack

### Frontend
- Next.js 15 + React 19 + TypeScript
- Tailwind CSS with dark/light theme
- Three.js + React Three Fiber for 3D visualization
- Lucide icons

### Backend
- Python 3.14 + FastAPI
- Pydantic for request/response validation
- NumPy for engineering calculations
- ezdxf for DXF drawing generation
- trimesh + shapely for 3D mesh generation
- Custom STEP (ISO 10303-21 AP214) exporter
- reportlab for PDF generation
- openpyxl for Excel export

## Testing

```powershell
cd backend
python -m pytest tests/ -v
```

Test suites:
- `test_calculations.py`: Engineering calculations (20 tests)
- `test_cad.py`: DXF, mesh, and STEP generation (15 tests)
- `test_api.py`: API endpoints (13 tests)

## CAD Engine Notes

- **FreeCAD**: Not available in this environment. STEP export uses a custom faceted approximation.
- **AutoCAD**: Not available. DWG is not supported. Use DXF or AutoCAD scripts.
- **OpenCASCADE (build123d/cadquery)**: Not available for Python 3.14. Custom STEP exporter provides faceted B-rep solids.

For true analytical B-rep STEP export, install FreeCAD or build123d. See `docs/deployment.md` for details.

## Known Limitations

1. Tooth geometry uses a simplified involute approximation (not manufacturing-accurate)
2. No load capacity, fatigue, or structural analysis performed
3. Material selections are proposed only, not verified
4. Bearing selection requires dedicated load and life analysis
5. Housing structural analysis (FEA) not performed
6. Thermal and lubrication analysis not performed
7. Manufacturing tolerances not specified
8. STEP export uses faceted (approximated) cylindrical surfaces
9. DWG format not available without AutoCAD
10. In-memory storage (no database) — state is lost on backend restart

## Project Structure

```
gearbox-studio/
├── README.md
├── .gitignore
├── frontend/          # Next.js + React frontend
│   ├── src/
│   │   ├── app/        # Pages (dashboard, new-design, etc.)
│   │   ├── components/ # UI components, 3D viewer, layout
│   │   ├── lib/        # API client, utilities
│   │   ├── hooks/      # React context/hooks
│   │   └── types/      # TypeScript types
│   └── public/
├── backend/           # FastAPI + Python backend
│   ├── app/
│   │   ├── api/        # Route handlers
│   │   ├── schemas/    # Pydantic models
│   │   ├── calculations/ # Engineering formulas
│   │   ├── cad/        # DXF, mesh, STEP generators
│   │   ├── exporters/  # BOM, reports, packages
│   │   ├── jobs/       # Job management
│   │   ├── validation/ # Design validation
│   │   └── services/   # Design orchestration
│   └── tests/
├── projects/          # Generated design files
├── scripts/           # Setup, start, validate scripts
└── docs/             # Architecture, assumptions, deployment
```

## License

This project is for educational and portfolio demonstration purposes.
