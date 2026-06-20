# =============================================================================
# Stage 1 — Build React frontend
# =============================================================================
FROM node:20-slim AS frontend-build

WORKDIR /build
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts

COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2 — Python backend + serve built frontend
# =============================================================================
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY api.py predictor.py generate_data.py groq_client.py train.py ./
COPY models/ models/
COPY data/ data/

# Train model if artifacts are missing (e.g. fresh clone without models/)
RUN test -f models/isolation_forest.pkl || (python generate_data.py && python train.py)

# Copy built frontend from stage 1
COPY --from=frontend-build /build/dist frontend/dist/

EXPOSE 8000
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]
