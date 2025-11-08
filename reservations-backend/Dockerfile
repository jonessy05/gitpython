# ============================================================
# 1️⃣ Build Stage — erstellt alle Python-Wheels inkl. Dependencies
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && pip install --upgrade pip \
    # Hier wichtig: ohne --no-deps bauen, damit auch Starlette usw. dazukommen
    && pip wheel -r requirements.txt -w /wheels \
    && apt-get purge -y build-essential \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# ============================================================
# 2️⃣ Runtime Stage — leichtes Produktionsimage
# ============================================================
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /wheels /wheels
COPY . /app

# jetzt alle Wheels (inkl. FastAPI + Starlette + Pydantic usw.) installieren
RUN pip install --no-cache-dir --no-index --find-links=/wheels -r requirements.txt

EXPOSE 80
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
