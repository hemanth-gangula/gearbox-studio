# Deployment Guide

## Local Development

### Prerequisites

- **Python 3.14+** (with pip)
- **Node.js 22+** (with npm)
- Windows, macOS, or Linux

### Quick Start

```powershell
# 1. Install dependencies
.\scripts\setup.ps1

# 2. Start both services
.\scripts\start.ps1

# 3. Open the application
# Frontend: http://localhost:3000
# Backend API docs: http://127.0.0.1:8000/docs
```

### Manual Setup

#### Backend

```powershell
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

#### Frontend

```powershell
cd frontend
npm install
npm run dev
```

### Environment Variables

The application uses sensible defaults for local development. No environment variables are required.

Optional configuration:
- `FRONTEND_PORT` — Frontend port (default: 3000)
- `BACKEND_PORT` — Backend port (default: 8000)
- `BACKEND_URL` — Backend URL for the frontend proxy (default: http://127.0.0.1:8000)

## Production Deployment

### Frontend (Vercel)

The Next.js frontend can be deployed to Vercel:

```bash
cd frontend
npm run build
# Deploy to Vercel via CLI or Git integration
```

**Important**: The frontend API proxy (`next.config.ts` rewrites) must be updated to point to the production backend URL instead of `http://127.0.0.1:8000`.

### Backend (Cloud Platform)

The FastAPI backend requires Python with CAD dependencies (ezdxf, trimesh, shapely, mapbox-earcut, reportlab, openpyxl). Suitable platforms:

1. **Docker container** (recommended): Package with all dependencies
2. **Python-capable cloud service**: AWS EC2, Google Cloud Run, Azure Container Apps
3. **Railway / Render**: Python application hosting

**Note**: Do not deploy the backend to serverless functions. The CAD generation pipeline is long-running (5-15 seconds) and requires persistent processes. Use a container or VM.

### Docker Compose (recommended for production)

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./projects:/app/projects
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      - backend
```

## CAD Engine Configuration

### Current Environment

- **DXF**: ezdxf (no external CAD engine required)
- **3D Mesh**: trimesh + shapely + mapbox-earcut (no external CAD engine required)
- **STEP**: Custom faceted exporter (no external CAD engine required)

### Optional: FreeCAD Integration

For true analytical B-rep STEP export, install FreeCAD:

1. Download FreeCAD from https://www.freecad.org/
2. Add FreeCAD's Python path to PYTHONPATH
3. The backend will automatically detect FreeCAD if available

### Optional: AutoCAD Integration

For DWG export or native AutoCAD automation:

1. Install AutoCAD on the server
2. Install `pywin32` Python package
3. The backend will detect AutoCAD COM automation if available

## Supported Export Formats

| Format | Status | Engine |
|--------|--------|--------|
| DXF | ✅ Full support | ezdxf |
| GLB | ✅ Full support | trimesh |
| STEP | ✅ Faceted approximation | Custom exporter |
| STL | ✅ Per-component | trimesh |
| CSV | ✅ Full support | Python stdlib |
| XLSX | ✅ Full support | openpyxl |
| PDF | ✅ Full support | reportlab |
| Markdown | ✅ Full support | Python stdlib |
| SCR | ✅ Full support | Custom generator |
| LSP | ✅ Full support | Custom generator |
| ZIP | ✅ Full support | Python stdlib |
| DWG | ❌ Not available | Requires AutoCAD |

## Troubleshooting

### Backend won't start
- Verify Python 3.14+ is installed: `python --version`
- Verify all dependencies: `pip install -r requirements.txt`
- Check port 8000 is not in use

### Frontend won't start
- Verify Node.js 22+ is installed: `node --version`
- Run `npm install` in the frontend directory
- Check port 3000 is not in use

### 3D model not loading
- Verify the backend is running and the GLB file was generated
- Check the browser console for errors
- Ensure the design has been generated (not just configured)

### DXF files are empty
- Verify ezdxf is installed correctly
- Check that the design generation completed successfully
- Verify files exist in `projects/{design_id}/`

### STEP file missing
- The custom STEP exporter may fail for edge cases
- Check the backend logs for errors
- The STEP format is best-effort; DXF and GLB are the primary formats
