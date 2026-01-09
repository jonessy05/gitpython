# Reservierungen Backend API

FastAPI REST API für die Verwaltung von Reservierungen mit JWT-Authentifizierung, PostgreSQL, Docker und Kubernetes.

**Stack:** Python 3.12 | FastAPI 0.121.1 | SQLAlchemy 2.0.23 | Pydantic 2.5.0 | PostgreSQL

---

## 🚀 Quick Start

### Voraussetzungen
- **Podman** oder **Docker**
- **Kind** (Kubernetes in Docker)
- **Kubectl**

### Container-Deployment (Local Development)

```bash
# Im reservations-backend Verzeichnis:
cd reservations-backend

# Image bauen
podman build -t localhost/reservations-backend:local-dev .

# Image in Kind-Cluster laden
podman save localhost/reservations-backend:local-dev --format oci-archive -o reservations-backend.tar
kind load image-archive reservations-backend.tar -n kind-cluster

# Kustomize anwenden
kubectl apply -k overlays/local --prune -l app.kubernetes.io/part-of=biletado -n biletado

# Deployment neu starten
kubectl rollout restart deployment reservations -n biletado

# Auf Ready-Status warten
kubectl wait pods -n biletado -l app.kubernetes.io/component=backend --for condition=Ready --timeout=120s
```

### Logs & Debugging
```bash
kubectl logs deployment/reservations -n biletado -f
kubectl port-forward -n biletado deployment/reservations 8000:8000
```

### 🐍 Python (Direkt, ohne Container)

```bash
python -m venv venv
source venv/bin/activate  # oder: venv\Scripts\activate (Windows)
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API unter: http://localhost:8000 | Docs: http://localhost:8000/docs

---

## 🔧 Konfigurationsparameter

Alle Konfigurationen werden über Umgebungsvariablen gesteuert. Hier ist die **zentrale Referenz**:

### 📋 Allgemeine Konfiguration

| Umgebungsvariable | Typ | Standard | Beschreibung | Erforderlich |
|---|---|---|---|---|
| `LOG_LEVEL` | string | `INFO` | Logging Level (DEBUG, INFO, WARNING, ERROR) | ❌ |
| `LOG_FORMAT` | string | `json` | Log Format (json oder text) | ❌ |
| `HOST` | string | `0.0.0.0` | Server Host/IP | ❌ |
| `PORT` | int | `8000` | Server Port | ❌ |

### 🔐 JWT-Authentifizierung (lokal)

| Umgebungsvariable | Typ | Standard | Beschreibung | Erforderlich |
|---|---|---|---|---|
| `SECRET_KEY` | string | `your-secret-key-change-in-production` | JWT Secret für lokale Token-Signierung | ✅* |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Token-Gültigkeit in Minuten | ❌ |
| `DISABLE_AUTH` | boolean | `false` | Auth deaktivieren (nur für Tests!) | ❌ |

**\* Pflichtfeld wenn Keycloak NICHT konfiguriert ist**

### 🔐 Keycloak-Integration (Optional)

| Umgebungsvariable | Typ | Standard | Beschreibung | Erforderlich |
|---|---|---|---|---|
| `JWT_ISSUER_URL` | string | nicht gesetzt | Keycloak OIDC Issuer URL (z.B. https://keycloak.example.com/auth/realms/biletado) | ❌** |
| `JWT_ALGORITHM` | string | `HS256` | JWT Algo (HS256 für lokal, RS256 für Keycloak) | ❌ |
| `JWT_AUDIENCE` | string | `reservations-api` | JWT Audience Claim | ❌ |

**\*\* Wenn gesetzt, wird Keycloak verwendet statt lokalem JWT**

### 🗄️ PostgreSQL-Datenbank

| Umgebungsvariable | Typ | Standard | Beschreibung | Erforderlich |
|---|---|---|---|---|
| `POSTGRES_RESERVATIONS_HOST` | string | `postgres` | Database Host | ❌ |
| `POSTGRES_RESERVATIONS_PORT` | int | `5432` | Database Port | ❌ |
| `POSTGRES_RESERVATIONS_DBNAME` | string | `reservations_v3` | Database Name | ❌ |
| `POSTGRES_RESERVATIONS_USER` | string | `postgres` | Database User | ❌ |
| `POSTGRES_RESERVATIONS_PASSWORD` | string | `postgres` | Database Password | ❌ |

### 🐳 Container-Beispiele

**Docker lokal starten:**
```bash
docker build -t reservations-backend:latest .
docker run -p 8000:80 \
  -e LOG_LEVEL=INFO \
  -e SECRET_KEY="secure-key-here" \
  -e POSTGRES_RESERVATIONS_HOST=postgres \
  -e POSTGRES_RESERVATIONS_PASSWORD=secure-password \
  reservations-backend:latest
```

**Alle Logs anzeigen:**
```bash
docker logs -f <container-id>
```

### ☸️ Kubernetes Konfiguration

Die Konfiguration erfolgt über `base/kustomization.yaml`:

```yaml
namespace: biletado
configMapGenerator:
  - name: reservations-config
    literals:
      - LOG_LEVEL=INFO
      - LOG_FORMAT=json
secretGenerator:
  - name: reservations-secrets
    literals:
      - SECRET_KEY="change-me-in-production"
```

**Mit Kustomize deployen:**
```bash
kubectl apply -k base/ -n biletado
kubectl logs -f deployment/reservations-backend -n biletado
```

---

## 📋 API Endpoints

### Health & Status
- `GET /health` - Health Check
- `GET /status` - API Status
- `GET /api/v3/reservations/health` - Service Health
- `GET /api/v3/reservations/status` - Service Status

### Reservierungen
- `GET /api/v3/reservations/reservations` - Alle Reservierungen abrufen
- `GET /api/v3/reservations/reservations/{id}` - Einzelne Reservierung
- `POST /api/v3/reservations/reservations` - Neue Reservierung erstellen
- `PUT /api/v3/reservations/reservations/{id}` - Reservierung aktualisieren/wiederherstellen
- `DELETE /api/v3/reservations/reservations/{id}` - Reservierung löschen (soft delete)

**Authentifizierung:** Alle POST/PUT/DELETE Endpoints benötigen ein gültiges JWT Token im `Authorization: Bearer <token>` Header

---

## 🧪 Testing

```bash
# Unit Tests ausführen
pytest tests/ -v

# Mit Coverage Report
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

**Automatisierte Tests:** GitHub Actions Pipeline prüft automatisch bei jedem Push:
- ✅ Code Quality (pylint, black, flake8)
- ✅ Unit Tests (pytest + Coverage)
- ✅ Security Scans (bandit, safety)
- ✅ Docker Build

Logs einsehen: Repository → Actions → [Run] → Jobs

---

## 📝 Logging

**Log-Ausgabe lokal:**
```bash
uvicorn app.main:app --reload --log-level debug
```

**Log-Level ändern:**
```bash
export LOG_LEVEL=DEBUG
python app/main.py
```

**In Kubernetes:**
```bash
kubectl logs -f deployment/reservations-backend -n biletado
kubectl logs deployment/reservations-backend -n biletado --tail=50
```

Alle Logs enthalten:
- ISO 8601 Timestamp (UTC)
- Log Level (DEBUG, INFO, WARNING, ERROR)
- Operation (CREATE, READ, UPDATE, DELETE)
- User ID & Object IDs
- JSON-Format für strukturierte Verarbeitung

---

## 🔐 Sicherheit

- **JWT-Authentifizierung** für alle sensiblen Endpoints
- **Token-Expiration** nach konfigurierbarer Zeit (Standard: 30 Min)
- **Pydantic Validierung** für alle Eingaben
- **SQLAlchemy ORM** verhindert SQL-Injection
- **Soft-Delete** für Audit Trail

---

## 📦 Abhängigkeiten

Siehe [reservations-backend/requirements.txt](requirements.txt) für vollständige Liste.

---

## 📄 Lizenz

MIT License - Copyright (c) 2025 jonessy05
