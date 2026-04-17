# =============================================================================
# Dockerfile — Multi-Stage Build for the FastAPI Application
# =============================================================================
# PURPOSE: Create a minimal, production-ready Docker image for the API service.
#
# Stage 1 (builder): Install all Python dependencies into the system Python.
#   This stage includes build tools needed to compile C extensions (e.g., bcrypt).
#
# Stage 2 (runtime): Copy only the installed packages and source code into a
#   clean slim image. No compilers or build tools in the final image.
#
# In development, docker-compose overrides the CMD and mounts the source code
# as a volume, so changes trigger Uvicorn's hot-reload automatically.
# =============================================================================

# ---------------------------------------------------------------------------
# STAGE 1: BUILDER
# ---------------------------------------------------------------------------
# PURPOSE: Install Python dependencies. This stage is discarded after build,
# so build tools don't bloat the final image.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Copy only the dependency file first to leverage Docker layer caching.
# Dependencies change less often than source code, so this layer is cached.
COPY pyproject.toml .

# Install build essentials (needed for compiling C extensions like bcrypt)
# then install the project dependencies.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .

# ---------------------------------------------------------------------------
# STAGE 2: RUNTIME
# ---------------------------------------------------------------------------
# PURPOSE: Minimal image with only the Python runtime, installed packages,
# and application source code. No compilers, no build tools.
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copy installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application source code
COPY . .

# Document the port the application listens on
EXPOSE 8000

# Default command for production (overridden by docker-compose in development)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
