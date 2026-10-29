FROM python:3.12-slim

# System libs for shapely (libgeos) and reportlab (libffi, gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libgeos-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python deps (cached layer — only rebuilt when requirements.txt changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY . .

# Default projects dir (overridden by PROJECTS_DIR env var)
RUN mkdir -p /tmp/projects

EXPOSE 8000

# Railway passes $PORT, Render passes $PORT too; fall back to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
