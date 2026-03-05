# ============================================
# Nyaya Mitra Backend - Production Dockerfile
# ============================================
# Multi-stage build for minimal image size

# Stage 1: Build dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim as production

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY . .

# Remove unnecessary files
RUN rm -rf tests/ __pycache__/ .pytest_cache/ \
    test_*.py *.md .env.example .env \
    chroma_db/ test_chroma_db/ test_rag_chroma_db/

# Create non-root user for security
RUN groupadd -r nyaya && useradd -r -g nyaya -d /app -s /sbin/nologin nyaya
RUN mkdir -p /app/generated_documents /app/chroma_db /app/uploads \
    && chown -R nyaya:nyaya /app

USER nyaya

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command with Gunicorn for production
CMD ["uvicorn", "main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--timeout-keep-alive", "120", \
     "--access-log", "-"]
