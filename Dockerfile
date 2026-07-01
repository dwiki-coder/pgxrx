# ============================================
# PGxRx - Pharmacogenomics Decision Tool
# Multi-stage Docker build
# ============================================

# --- Stage 1: Build ---
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /build

# Install system deps needed for building C extensions
RUN apt-get update && apt-get install -y --no-install-recommend \
        build-essential \
        libffi-dev \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libcairo2 \
        libgirepository1.0-dev \
        gcc \
        && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[all]"

# --- Stage 2: Runtime ---
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PGXRX_DATA_DIR="/app/data"

# Runtime system deps
RUN apt-get update && apt-get install -y --no-install-recommend \
        libffi7 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libcairo2 \
        libgomp1 \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy built package from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . /app/

# Create runtime user
RUN useradd --create-home pgxrx
RUN chown -R pgxrx:pgxrx /app
USER pgxrx

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD pgxrx health || exit 1

ENTRYPOINT ["pgxrx"]
CMD ["--help"]
