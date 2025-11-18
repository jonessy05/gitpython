# Reservierungen Backend API

FastAPI-basierte REST API für die Verwaltung von Reservierungen mit JWT-Authentifizierung, vollständiger CI/CD-Pipeline, containerisiertem Deployment und umfassender Logging-Unterstützung.

**Projektübersicht:**
- 🎯 **Zweck:** REST API für Reservierungsverwaltung
- 🛠️ **Stack:** Python 3.12 + FastAPI + Pydantic
- 📦 **Deployment:** Docker Container + Kubernetes
- 🔒 **Sicherheit:** JWT-Authentication + HTTPS-ready
- 📊 **Quality:** GitHub Actions CI/CD mit vollständiger Pipeline
- 📝 **Logging:** Strukturiert auf allen Ebenen (lokal, Container, K8s)

## 🎯 Features

- ✅ **REST API** mit FastAPI v0.121.1
- ✅ **JWT-Authentifizierung** mit python-jose für sichere Endpoints
- ✅ **OpenAPI 3.1 Dokumentation** (automatisch generiert via Swagger/ReDoc)
- ✅ **CRUD-Operationen** für Reservierungen
- ✅ **Containerisierung** mit Docker Multi-Stage Build
- ✅ **Kubernetes Deployment** mit Kustomize
- ✅ **Health Check Endpoint** für Container-Orchestrierung
- ✅ **Pydantic v2.5.0 Validierung** für Datenintegrität
- ✅ **Strukturiertes Logging** mit Timestamps und Log-Levels
- ✅ **GitHub Actions CI/CD Pipeline** mit Lint, Test, Security, Build
- ✅ **Automatisierte Tests** mit pytest und Code-Coverage

## 📋 API Endpoints

### Authentifizierung
- `POST /auth/token` - JWT Token generieren (zum Testen)

### Reservierungen (Auth erforderlich)
- `GET /reservations` - Alle Reservierungen abrufen
- `GET /reservations/{id}` - Einzelne Reservierung abrufen
- `POST /reservations` - Neue Reservierung erstellen
- `PUT /reservations/{id}` - Reservierung aktualisieren
- `PATCH /reservations/{id}/status` - Status aktualisieren
- `DELETE /reservations/{id}` - Reservierung löschen

### System
- `GET /health` - Health Check
- `GET /` - API Info
- `GET /docs` - Interaktive Swagger UI
- `GET /redoc` - ReDoc Dokumentation
- `GET /openapi.json` - OpenAPI Schema

## ✅ Erfüllung der Anforderungen

| Kriterium | Umsetzung | Details |
|-----------|-----------|---------|
| **Programmiersprache** | Python 3.12 | Exklusiv, einzige getestete Version |
| **Framework** | FastAPI v0.121.1 | Modern, performant, integrierte OpenAPI-Docs |
| **ORM/Datenvalidierung** | Pydantic v2.5.0 | Typsichere Datenvalidierung, Prepared Statements (In-Memory) |
| **Authentifizierung** | JWT mit python-jose | Token-basiert, 30min Gültigkeit |
| **API-Dokumentation** | OpenAPI 3.1 (auto) | Swagger UI + ReDoc |
| **Containerisierung** | Docker Multi-Stage | Python 3.12-slim, optimiert |
| **Orchestrierung** | Kubernetes + Kustomize | Production-ready Deployment-Konfiguration |
| **CI/CD Pipeline** | GitHub Actions | Lint, Test, Security, Build Jobs |
| **Logging** | Strukturiert (Timestamps) | DEBUG/INFO/WARNING/ERROR Levels |
| **Tests** | pytest + Coverage | Unit Tests mit Code-Coverage Reports |
| **Codequalität** | pylint, black, flake8 | Automatisiert in Pipeline |

---

## 🚀 Quick Start (5 Minuten)

```bash
# 1. In das Verzeichnis wechseln
cd reservations-backend

# 2. Virtuelle Umgebung erstellen & aktivieren
python -m venv venv
venv\Scripts\activate  # Windows

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Server starten
uvicorn app.main:app --reload --port 8000

# 5. API öffnen
# Browser: http://localhost:8000/docs (Swagger UI mit Test-Interface)
```

**Das war's!** Die API läuft lokal mit Logs in der Console.

---

## 🚀 Lokale Entwicklung

### Voraussetzungen
- Python 3.12+ (einzig unterstützte Version)
- pip
- Optional: Docker/Podman für Container-Testing

### Installation

```bash
cd reservations-backend

# Virtuelle Umgebung erstellen
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Dependencies installieren
pip install -r requirements.txt

# Server starten
uvicorn app.main:app --reload --port 8000
```

Die API ist dann verfügbar unter:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🐳 Container-Deployment

### Image bauen (Podman/Docker)

```bash
cd reservations-backend
podman build -t reservations-backend:latest .
# oder: docker build -t reservations-backend:latest .
```

**Multi-Stage Build Details:**
- Stage 1: Builder - installiert Dependencies
- Stage 2: Runtime - Production-Image mit uvicorn ASGI Server
- Basis-Image: `python:3.12-slim` (optimiert für Größe)

### Container starten mit Logging

```bash
# Mit Logs in Container (werden zu stdout gestreamt)
podman run -p 8000:80 \
  -e LOG_LEVEL=INFO \
  -e SECRET_KEY="your-secret-key" \
  reservations-backend:latest

# Log-Output folgen
podman logs -f <container-id>
```

### Wichtige Container-Environment-Variablen

| Variable | Standard | Beschreibung |
|----------|----------|-------------|
| `LOG_LEVEL` | `INFO` | DEBUG, INFO, WARNING, ERROR |
| `SECRET_KEY` | Pflichtfeld | JWT Secret (mind. 32 Zeichen in Produktion) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token-Gültigkeit |
| `HOST` | `0.0.0.0` | Bind Address |
| `PORT` | `80` | Container Port |

## ☸️ Kubernetes Deployment

### Voraussetzungen
- kubectl installiert
- kind Cluster oder anderer K8s Cluster
- Namespace `biletado` erstellt

### Image in kind laden

```bash
# Image bauen
podman build -t reservations-backend:latest .

# Image als Archiv speichern und in kind laden
podman save reservations-backend:latest --format oci-archive -o reservations-backend.tar
kind load image-archive reservations-backend.tar -n kind-cluster
```

### Mit Kustomize deployen

```bash
cd reservations-backend/k8s

# Deployen
kubectl apply -k . -n biletado

# Status prüfen
kubectl get pods -n biletado -l app=reservations-backend
kubectl wait pods -n biletado -l app=reservations-backend --for condition=Ready --timeout=120s

# Logs anzeigen
kubectl logs -n biletado -l app=reservations-backend --tail=50 -f
```

### Service testen

Port-Forwarding einrichten:
```bash
kubectl port-forward -n biletado service/reservations-backend 8000:8000
```

Dann API unter http://localhost:8000 aufrufen.

### Image nach Code-Änderungen aktualisieren

```bash
# Im reservations-backend Verzeichnis
export TAG="reservations-backend:latest"
podman build -t "$TAG" .
kind load image-archive -n kind-cluster <(podman save "$TAG" --format oci-archive)
kubectl rollout restart deployment reservations-backend -n biletado
kubectl rollout status deployment reservations-backend -n biletado
```

## 🔄 GitHub Actions CI/CD Pipeline

Das Projekt nutzt GitHub Actions für vollständige Qualitätssicherung und Deployment-Automation.

### Pipeline-Übersicht

Die Pipeline besteht aus 4 parallel-laufenden Jobs, die nur bei Änderungen an relevanten Dateien triggern:

```
┌─────────────────────────────────────────────────────────┐
│  GitHub Push oder Pull Request                          │
└──────────────────────┬──────────────────────────────────┘
                       │
         ┌─────────────┼─────────────┬──────────────┐
         │             │             │              │
    ┌────▼────┐  ┌────▼────┐  ┌────▼────┐  ┌────▼────┐
    │  Lint   │  │  Tests  │  │Security │  │  Build  │
    └─────────┘  └─────────┘  └─────────┘  └─────────┘
```

### 1️⃣ **Lint Workflow** (`.github/workflows/lint.yml`)

**Trigger:** Push/PR mit Änderungen in `app/**` oder `requirements.txt`

**Python 3.12 Qualitätschecks:**
- ✅ **pylint**: Code-Analyse (max-line-length: 120)
- ✅ **black**: Code-Formatierung (automatisch)
- ✅ **flake8**: PEP8 Compliance

**Ausgabe:** Automatischer PR-Comment mit Ergebnissen

### 2️⃣ **Test Workflow** (`.github/workflows/tests.yml`)

**Trigger:** Push/PR mit Änderungen in `app/**`, `tests/**`, oder `requirements.txt`

**Auf Python 3.12 Standardmäßig:**
- ✅ **pytest**: Unit Tests mit Verbose Output
- ✅ **pytest-cov**: Code Coverage Analyse
- ✅ **Codecov Integration**: Coverage Reports als Artifacts

**Coverage-Reports:**
- Terminal-Output: `--cov-report=term`
- XML-Report: `--cov-report=xml` (für Codecov)
- HTML-Report: `--cov-report=html` (uploadbar als Artifact)

**Test-Artefakte:**
- Coverage Reports in `reservations-backend/htmlcov/`
- 30 Tage Retention

### 3️⃣ **Security Workflow** (`.github/workflows/security.yml`)

**Trigger:** Push/PR mit Änderungen in `reservations-backend/**`

**Security Scans auf Python 3.12:**
- ✅ **bandit**: Findet häufige Sicherheitsprobleme
- ✅ **safety**: Dependency Vulnerability Check
- ✅ **OWASP Dependency-Check**: Container-spezifische Schwachstellen

**Sicherheits-Artefakte:**
- `bandit-report.json`
- `safety-report.json`
- `dependency-check-report.json`

### 4️⃣ **Build Workflow** (`.github/workflows/build.yml`)

**Trigger:** Push/PR/Tag mit Änderungen in `reservations-backend/**` oder `.github/workflows/build.yml`

**Docker Image Build:**
- Python 3.12 Multi-Stage Build
- Layer Caching für schnellere Builds
- Push zu ghcr.io (GitHub Container Registry)

**Image-Tags:**
- `latest` für main-Branch
- `<branch-name>` für feature-Branches
- `v*` semantische Versioning für Tags
- `<commit-sha>` für Traceability

**Automatisierter PR-Comment:**
- ✅ "Docker image built successfully for this PR!"

---

### Manuelle Workflow-Ausführung

**In GitHub UI:**
```
Repository → Actions → [Workflow Name] → Run workflow
```

**Mit GitHub CLI:**
```bash
gh workflow run lint.yml --ref main
gh workflow run tests.yml --ref develop
```

### Status und Logs prüfen

**GitHub UI:**
```
Repository → Actions → [Run] → Jobs → [Job Name]
```

**GitHub CLI:**
```bash
gh run list
gh run view <RUN_ID>
gh run view <RUN_ID> --log
```

---

## 🧪 Testing

### Unit Tests lokal ausführen

```bash
cd reservations-backend

# Alle Tests ausführen
pytest tests/ -v

# Mit Coverage Report
pytest tests/ --cov=app --cov-report=html

# Nur spezifische Test-Datei
pytest tests/test_models.py -v

# Mit detailliertem Output
pytest tests/ -v --tb=long
```

### Automatisierte Tests in der CI/CD Pipeline

Die GitHub Actions Pipeline führt automatisch folgende Tests aus:

**Test Workflow Ablauf:**
```
1. pytest wird mit Coverage aktiviert
2. Tests laufen gegen Python 3.12
3. Coverage Reports werden generiert (HTML + XML)
4. Codecov Integration lädt XML-Reports hoch
5. HTML-Reports als Artifacts (30 Tage)
```

**Pytest Konfiguration (pytest.ini):**

## 📝 Strukturiertes Logging

Das System bietet umfassendes Logging auf mehreren Ebenen für Debugging und Monitoring.

### Log-Format

```
[2025-11-18T10:30:45.123456Z] [INFO] [reservations.py:42] - GET /reservations - User: user@example.com - Status: 200
[2025-11-18T10:30:46.234567Z] [INFO] [reservations.py:67] - POST /reservations - Created: ID=123 - Status: 201
[2025-11-18T10:30:47.345678Z] [WARNING] [auth.py:15] - Token validation failed - Invalid signature
[2025-11-18T10:30:48.456789Z] [ERROR] [main.py:88] - Database connection error - Connection refused
```

**Format:** `[ISO-TIMESTAMP] [LEVEL] [MODULE:LINE] - MESSAGE`

### Log-Level Konfiguration

```bash
# Lokal
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# In Docker
podman run -e LOG_LEVEL=DEBUG reservations-backend:latest

# In Kubernetes (kustomization.yaml)
configMapGenerator:
  - name: reservations-config
    literals:
      - LOG_LEVEL=DEBUG

# In der Anwendung
import logging
logger = logging.getLogger(__name__)
logger.info("Reservierung erstellt")
logger.error("Fehler beim Abrufen der Reservierung")
```

### Logs abrufen

#### Lokal (uvicorn Server):
```bash
cd reservations-backend
uvicorn app.main:app --reload --log-level info
# Logs erscheinen direkt in der Console
```

#### Docker Container:
```bash
# Live Logs folgen
docker logs -f <container-id>

# Letzte 50 Zeilen
docker logs --tail 50 <container-id>

# Mit Timestamps
docker logs --timestamps <container-id>
```

#### Kubernetes Pod:
```bash
# Logs anzeigen
kubectl logs -f deployment/reservations-backend -n biletado

# Vorherige Logs (falls Pod neu gestartet wurde)
kubectl logs -p deployment/reservations-backend -n biletado

# Mit Timestamp
kubectl logs deployment/reservations-backend -n biletado --timestamps=true
```

### Audit-Logging für schreibende Operationen

Alle CREATE, UPDATE, DELETE Operationen werden gelogged:

```
[2025-11-18T10:30:45.123456Z] [INFO] [audit] - Operation: CREATE
  - Entity: Reservation
  - ID: 42
  - User: john@example.com
  - Data: {customer_name: "Max Mustermann", party_size: 4}
  - Status: 201

[2025-11-18T10:30:50.234567Z] [INFO] [audit] - Operation: UPDATE
  - Entity: Reservation
  - ID: 42
  - User: john@example.com
  - Changes: {status: "pending" → "confirmed"}
  - Status: 200
```

### Container-integrierte Logs

Das Container-System kann Logs automatisch:
- ✅ Zu stdout/stderr streamen (Docker/Podman logs lesen)
- ✅ Mit Timestamps versehen
- ✅ Nach Log-Level filtern
- ✅ In ELK Stack, Splunk, Datadog integrieren

---

## 🧪 API Testing & Authentifizierung

### 1. Token generieren

```bash
curl -X POST "http://localhost:8000/auth/token?username=testuser"
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. Reservierungen abrufen (mit Token)

```bash
TOKEN="<dein-token-hier>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/reservations
```

### 3. Neue Reservierung erstellen

```bash
TOKEN="<dein-token-hier>"
curl -X POST "http://localhost:8000/reservations" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Max Mustermann",
    "customer_email": "max@example.com",
    "reservation_date": "2025-12-24T18:00:00Z",
    "party_size": 4,
    "special_requests": "Fensterplatz bitte"
  }'
```

### 4. Mit Swagger UI testen (Empfohlen!)

1. Öffne http://localhost:8000/docs
2. Klicke auf "Authorize" 🔓
3. Generiere zuerst einen Token mit `/auth/token`
4. Kopiere den `access_token` Wert
5. Gib ihn im Authorization Dialog ein
6. Teste die Endpoints direkt in der UI

## 🔧 Konfiguration

### Umgebungsvariablen

Alle Konfigurationsparameter werden über Umgebungsvariablen gesteuert:

| Variable | Beschreibung | Standardwert | Erforderlich |
|----------|-------------|-------------|-------------|
| `SECRET_KEY` | JWT Secret für Token-Signierung (lokal) | `your-secret-key-change-in-production` | Nein* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token Gültigkeit in Minuten | `30` | Nein |
| `LOG_LEVEL` | Logging Level (DEBUG, INFO, WARNING, ERROR) | `INFO` | Nein |
| `JWT_ALGORITHM` | JWT Algorithmus (HS256 für lokal, RS256 für Keycloak) | `HS256` | Nein |
| `JWT_AUDIENCE` | JWT Audience (Zielgruppe des Tokens) | `reservations-api` | Nein |
| `JWT_ISSUER_URL` | Keycloak OIDC Issuer URL | Nicht gesetzt (local mode) | Nein** |

**Hinweise:**
- `*` `SECRET_KEY` ist nur erforderlich wenn Keycloak NICHT konfiguriert ist (lokales JWT)
- `**` Wenn `JWT_ISSUER_URL` gesetzt ist, wird Keycloak verwendet; sonst lokale JWT-Validierung

### Keycloak Integration

Für die Integration mit Keycloak als OIDC Provider:

```bash
# Beispiel: Umgebungsvariablen setzen
export JWT_ISSUER_URL=https://keycloak.example.com/auth/realms/biletado
export JWT_ALGORITHM=RS256
export JWT_AUDIENCE=reservations-api
```

Die Anwendung wird dann:
1. Beim Start die JWKS (öffentliche Keys) von Keycloak laden
2. Bei jedem Request den JWT Token gegen diese Keys validieren
3. Ablaufdatum und Issuer prüfen

#### Keycloak Setup

1. **Realm erstellen**: `biletado`
2. **Client erstellen**:
   - Name: `reservations-api`
   - Access Type: `bearer-only`
3. **Mapper für 'sub' Claim** (falls nötig):
   - Protocol Mapper: `User Property`
   - Property: `username`
   - Token Claim Name: `sub`

#### Token für Testing

```bash
# Keycloak Token mit Curl abrufen
curl -X POST \
  https://keycloak.example.com/auth/realms/biletado/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=reservations-api" \
  -d "username=testuser" \
  -d "password=password123"

# Dann den access_token verwenden:
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/reservations
```

### Kubernetes Secret

Das Secret für den JWT Key wird in `k8s/secret.yaml` definiert:

```yaml
stringData:
  SECRET_KEY: "change-this-secret-key-in-production-use-strong-random-value"
```

**⚠️ WICHTIG:** Für Produktion einen sicheren, zufälligen Wert verwenden!

## 🔐 Authentifizierung & Sicherheit

### Lokale Entwicklung (Ohne Keycloak)

```bash
# 1. Token generieren
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token?username=testuser" | jq -r '.access_token')

# 2. Token nutzen
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/reservations
```

### Production (Mit Keycloak)

- `JWT_ISSUER_URL` muss auf deinen Keycloak Server zeigen
- Tokens werden gegen öffentliche Keys von Keycloak validiert
- Token Expiration wird geprüft
- Audience ('aud' Claim) wird validiert

## 📁 Projektstruktur

```
reservations-backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI App & Root Endpoints
│   ├── auth.py              # JWT Token Handling
│   ├── models.py            # Pydantic Models
│   └── routes/
│       ├── __init__.py
│       └── reservations.py  # Reservierungs-Endpoints
├── k8s/
│   ├── deployment.yaml      # K8s Deployment
│   ├── service.yaml         # K8s Service
│   ├── secret.yaml          # K8s Secret für JWT
│   └── kustomization.yaml   # Kustomize Config
├── Dockerfile               # Multi-Stage Docker Build
├── requirements.txt         # Python Dependencies
├── openapi.yaml            # OpenAPI Spezifikation
└── README.md               # Diese Datei
```

## 🎓 Datenmodell

### Reservation

```python
{
  "id": 1,
  "customer_name": "Max Mustermann",
  "customer_email": "max@example.com",
  "reservation_date": "2025-12-24T18:00:00Z",
  "party_size": 4,
  "special_requests": "Fensterplatz bitte",
  "status": "confirmed",  # pending | confirmed | cancelled | completed
  "created_at": "2025-11-05T10:00:00Z",
  "updated_at": "2025-11-05T10:00:00Z"
}
```

## 🔐 Sicherheit

- **JWT-Authentifizierung**: Alle `/reservations` Endpoints sind geschützt
- **Token Expiration**: Tokens laufen nach 30 Minuten ab
- **HTTPBearer Schema**: Standard-konforme Authentifizierung
- **Pydantic Validierung**: Input-Validierung für alle Requests

## 📝 Hinweise

- **In-Memory DB**: Aktuell werden Daten nur im Speicher gehalten (bei Neustart verloren)
- **Test-Auth**: `/auth/token` ist nur für Tests gedacht, keine echte Passwort-Authentifizierung
- **Produktion**: Für Produktion echte Datenbank (PostgreSQL, MongoDB) und echte Auth implementieren

## 🛠️ Entwickelt mit

- [FastAPI](https://fastapi.tiangolo.com/) - Modern, fast web framework
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [python-jose](https://github.com/mpdavis/python-jose) - JWT handling
- [uvicorn](https://www.uvicorn.org/) - ASGI server

## 📄 Lizenz

MIT License
