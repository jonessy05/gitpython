# ============================================================
# Multi-Stage Dockerfile for Reservierungen API
# Optimized for production with minimal size and security
# ============================================================

# ============================================================
# 1️⃣ Build Stage — Build Python wheels with all dependencies
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and build wheels
COPY requirements.txt .
RUN pip install --upgrade pip wheel && \
    pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# ============================================================
# 2️⃣ Runtime Stage — Minimal production image
# ============================================================
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    mkdir -p /app /app/logs && \
    chown -R appuser:appuser /app

WORKDIR /app

# Copy wheels from builder stage
COPY --from=builder /wheels /wheels

# Install runtime dependencies from wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt && \
    rm -rf /wheels /root/.cache

# Copy application code
COPY --chown=appuser:appuser app/ /app/app/

# Switch to non-root user
USER appuser

# Expose application port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

