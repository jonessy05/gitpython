# Reservierungen Backend API

FastAPI-basierte REST API für die Verwaltung von Reservierungen mit JWT-Authentifizierung.

## 🎯 Features

- ✅ **REST API** mit FastAPI
- ✅ **JWT-Authentifizierung** für sichere Endpoints
- ✅ **OpenAPI 3.1 Dokumentation** (automatisch generiert)
- ✅ **CRUD-Operationen** für Reservierungen
- ✅ **Docker Support** mit Multi-Stage Build
- ✅ **Kubernetes Deployment** mit Kustomize
- ✅ **Health Check Endpoint**
- ✅ **Pydantic Validierung**

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

## 🚀 Lokale Entwicklung

### Voraussetzungen
- Python 3.11+
- pip

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

## 🐳 Docker

### Image bauen

```bash
cd reservations-backend
podman build -t reservations-backend:latest .
# oder: docker build -t reservations-backend:latest .
```

### Container starten

```bash
podman run -p 8000:80 reservations-backend:latest
# oder: docker run -p 8000:80 reservations-backend:latest
```

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

## 🔄 CI/CD mit GitHub Actions

### Verfügbare Workflows

Das Projekt nutzt GitHub Actions für automatisierte Qualitätssicherung und Deployment:

#### 1. **Lint Workflow** (`.github/workflows/lint.yml`)
- Läuft bei: Push/PR auf `main` oder `develop`
- Prüft: pylint, black, flake8
- Artifacts: Lint Reports

```yaml
# Automatisch bei Push/PR
git push origin feature/my-feature
# → Lint Workflow wird automatisch gestartet
```

#### 2. **Test Workflow** (`.github/workflows/tests.yml`)
- Läuft bei: Push/PR auf `main` oder `develop`
- Matrix-Build: Python 3.11 + 3.12
- Coverage: Codecov Integration
- Artifacts: Coverage Reports

```yaml
# Automatisch bei Push/PR
git push origin feature/my-feature
# → Tests für Python 3.11 und 3.12
# → Coverage Report uploaded zu Codecov
```

#### 3. **Security Workflow** (`.github/workflows/security.yml`)
- Läuft bei: Push/PR + wöchentliche Schedule
- Scans: Bandit, Safety, Dependency-Check
- Artifacts: Security Reports

#### 4. **Build Workflow** (`.github/workflows/build.yml`)
- Läuft bei: Push/PR/Tag auf `main`, `develop`
- Baut: Docker Image für ghcr.io
- Caching: Layer Caching für schnellere Builds
- Tags: `latest`, `<branch>`, `<version>`, `sha-<hash>`

#### 5. **Complete CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
- Kombiniert: Lint → Test → Security → Build
- Status Check: Zeigt Overall-Status an
- Dependencies: Jobs warten aufeinander

#### 6. **Deploy Workflow** (`.github/workflows/deploy.yml`)
- Läuft bei: Push auf `main`, Tags `v*`
- Deployment: Zu Kubernetes mit Kustomize
- Smoke Tests: Health Check nach Deployment
- Notifications: Slack Alerts bei Fehlern

### Secrets konfigurieren

Für Deployments und Registry-Zugriff müssen folgende Secrets gespeichert werden:

```
GitHub Settings → Secrets and variables → Actions:

KUBE_CONFIG          # Base64-encoded kubeconfig für K8s
SLACK_WEBHOOK        # Optional: Slack Notifications
DOCKER_USERNAME      # Optional: Docker Hub Username
DOCKER_PASSWORD      # Optional: Docker Hub Token
```

**KUBE_CONFIG vorbereiten:**
```bash
# Base64 encode deinen kubeconfig
cat ~/.kube/config | base64 -w 0

# Dann in GitHub Secrets einfügen
```

### Workflow Status prüfen

```
GitHub UI:
  Repository → Actions → [Workflow Name]
  
  oder mit GitHub CLI:
  gh run list
  gh run view <RUN_ID>
  gh run view <RUN_ID> --log
```

### Automatische PR-Comments

Die Workflows kommentieren automatisch PRs mit Status-Updates:
- ✅ Lint completed
- ✅ Tests passed with coverage
- 🔒 Security scan completed
- 🐳 Docker image built
- 🚀 Deployed successfully

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

### Automatisierte Tests im CI/CD

Die GitLab CI/CD Pipeline führt automatisch folgende Tests aus:

```yaml
stages:
  - lint        # pylint, black
  - test        # pytest Unit Tests
  - build       # Docker Image Build
  - scan        # Container & Dependency Scanning
```

Siehe `.gitlab-ci.yml` für Details.

## 📝 Logging

### Logs anzeigen

#### Lokal entwickelt:
```bash
# Container Log ansehen
docker logs <container-id> -f

# Oder Log-Datei im Container:
docker exec <container-id> tail -f /app/logs/reservations_api.log
```

#### In Kubernetes:
```bash
# Pod Logs anzeigen
kubectl logs -f deployment/reservations-backend -n biletado

# Mit Timestamp
kubectl logs deployment/reservations-backend -n biletado --timestamps
```

### Audit-Logs

Alle schreibenden Operationen (CREATE, UPDATE, DELETE) werden als Audit-Logs erfasst:

```
[2025-11-05T10:30:45.123456] [INFO] [operation:CREATE] [user:john@example.com] [object:reservation] [id:42] - Created reservation for Max Mustermann
```

Format: `[TIMESTAMP] [LEVEL] [operation:OP] [user:USERID] [object:TYPE] [id:ID] - MESSAGE`

### Logging Level konfigurieren

```bash
# Environment Variable setzen
export LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR

# In Docker
docker run -e LOG_LEVEL=DEBUG reservations-backend:latest

# In Kubernetes kustomization.yaml
configMapGenerator:
  - name: reservations-config
    literals:
      - LOG_LEVEL=DEBUG
```

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

### 4. Mit Swagger UI testen

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
