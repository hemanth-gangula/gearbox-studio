FROM python:3.12-slim

# System deps for shapely, trimesh, reportlab
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgeos-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Projects dir (override via PROJECTS_DIR env var on Railway/Render)
RUN mkdir -p /app/projects

EXPOSE 8000

# PORT env var is set by Railway automatically; default to 8000 elsewhere
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
