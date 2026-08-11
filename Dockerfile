# syntax=docker/dockerfile:1

# =========================================================
# Stage 1 — Build the React frontend into static files
# =========================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Install deps first (better layer caching)
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Build
COPY frontend/ ./
RUN npm run build

# =========================================================
# Stage 2 — Python runtime, backend + built frontend only
# =========================================================
FROM python:3.11-slim AS runtime

# Keep the image lean and predictable
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# PyMuPDF needs no extra system libs on slim, but keep this minimal
# in case future deps need build tools; remove build-essential after use.
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python deps first for layer caching
COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential

# Copy backend source
COPY backend/ ./

# Drop dev/test/notebook helper files that don't need to ship in the image
RUN rm -rf Resources

# Copy the built frontend into ./static (served by FastAPI, see main.py)
COPY --from=frontend-builder /frontend/build ./static

# Hugging Face Spaces (Docker SDK) expects the app to listen on 7860,
# and requires the container to run as a non-root user with a writable
# home/working directory.
RUN useradd -m -u 1000 appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appuser /app
USER appuser

ENV PORT=7860
EXPOSE 7860

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
