# Biletado - Reservation API

FastAPI REST API for managing reservations with JWT authentication, PostgreSQL, Docker, and Kubernetes.

Built as a project for the Web Engineering 2 course at DHBW Karlsruhe.

## Project Overview

**Technology Stack:**
- Backend: Python 3.12 | FastAPI 0.121.1
- ORM: SQLAlchemy 2.0.23
- Validation: Pydantic 2.5.0
- Database: PostgreSQL
- Infrastructure: Kubernetes via Kustomize
- Identity Management: Keycloak (optional)
- API Documentation: Swagger (OpenAPI)

---

## Getting Started

### Prerequisites
- **Podman** Desktop or **Docker**
- **Kind** (Kubernetes in Docker)
- **kubectl** and **kustomize**

---
## Deployment Scenarios

### 1. Local Development

**Clone the repository:**
```bash
git clone git@github.com:jonessy05/gitpython.git
cd reservations-backend
```

**Ensure your Kubernetes cluster is running:**
```bash
kind get clusters
```

**Deploy to Kubernetes Cluster**

1. Build the image:
```bash
cd reservations-backend
podman build -t localhost/reservations-backend:local-dev .
```

2. Load the image into the Kind cluster:
```bash
podman save localhost/reservations-backend:local-dev --format oci-archive -o reservations-backend.tar
kind load image-archive reservations-backend.tar -n kind-cluster
```

3. Apply Kustomize overlays:
```bash
kubectl apply -k overlays/local --prune -l app.kubernetes.io/part-of=biletado -n biletado
```

4. Restart the deployment:
```bash
kubectl rollout restart deployment reservations -n biletado
```

5. Wait for the pods to be ready:
```bash
kubectl wait pods -n biletado -l app.kubernetes.io/component=backend --for condition=Ready --timeout=120s
```

**Access the service:**
```bash
kubectl port-forward -n biletado deployment/reservations 8000:8000
```

API available at: http://localhost:8000

**View logs:**
```bash
kubectl logs deployment/reservations -n biletado -f
```

---

### 2. Deploy to Existing Kubernetes Cluster

If you have an existing Biletado instance running in Kubernetes, clone the repository and apply the Kustomize overlays:

```bash
git clone git@github.com:jonessy05/gitpython.git
cd reservations-backend
kubectl apply -k overlays/local --prune -l app.kubernetes.io/part-of=biletado -n biletado
```

---

### 3. Deploy Pipeline-Generated Image

Deploy a CI/CD-built image into your local kind cluster using manual steps.

Prerequisites: `podman` (or Docker), `kind`, `kubectl` in PATH

1. Pull the image from the registry:
```bash
podman pull ghcr.io/jonessy05/gitpython/reservations-api:latest
```

2. Save and load the image into Kind:
```bash
podman save ghcr.io/jonessy05/gitpython/reservations-api:latest --format oci-archive -o reservations-cicd.tar
kind load image-archive reservations-cicd.tar -n kind-cluster
```

3. Apply the CI/CD overlay and restart the deployment:
```bash
kubectl apply -k overlays/cicd --prune -l app.kubernetes.io/part-of=biletado -n biletado
kubectl rollout restart deployment reservations -n biletado
kubectl wait pods -n biletado -l app.kubernetes.io/component=backend --for condition=Ready --timeout=120s
```

**Access the service:**
```bash
kubectl port-forward -n biletado deployment/reservations 8000:8000
```

API available at: http://localhost:8000

**View logs:**
```bash
kubectl logs deployment/reservations -n biletado -f
```

---

## Configuration Parameters

All configurations are controlled via environment variables. This document serves as the **central reference**.

### General Configuration

| Variable | Type | Default | Description | Required |
|---|---|---|---|---|
| `LOG_LEVEL` | string | `INFO` | Logging Level (DEBUG, INFO, WARNING, ERROR) | No |
| `LOG_FORMAT` | string | `json` | Log Format (json or text) | No |
| `HOST` | string | `0.0.0.0` | Server Host/IP | No |
| `PORT` | int | `8000` | Server Port | No |

### JWT Authentication (Local)

| Variable | Type | Default | Description | Required |
|---|---|---|---|---|
| `SECRET_KEY` | string | `your-secret-key-change-in-production` | JWT Secret for local token signing | Yes **\*** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | int | `30` | Token validity in minutes | No |
| `DISABLE_AUTH` | boolean | `false` | Disable authentication (tests only!) | No |

**\* Required if Keycloak is NOT configured**

### Keycloak Integration (Optional)

| Variable | Type | Default | Description | Required |
|---|---|---|---|---|
| `JWT_ISSUER_URL` | string | not set | Keycloak OIDC Issuer URL (e.g., https://keycloak.example.com/auth/realms/biletado) | No **\*\*** |
| `JWT_ALGORITHM` | string | `HS256` | JWT Algorithm (HS256 for local, RS256 for Keycloak) | No |
| `JWT_AUDIENCE` | string | `reservations-api` | JWT Audience Claim | No |

**\*\* If set, Keycloak will be used instead of local JWT**

### PostgreSQL Database

| Variable | Type | Default | Description | Required |
|---|---|---|---|---|
| `POSTGRES_RESERVATIONS_HOST` | string | `postgres` | Database Host | No |
| `POSTGRES_RESERVATIONS_PORT` | int | `5432` | Database Port | No |
| `POSTGRES_RESERVATIONS_DBNAME` | string | `reservations_v3` | Database Name | No |
| `POSTGRES_RESERVATIONS_USER` | string | `postgres` | Database User | No |
| `POSTGRES_RESERVATIONS_PASSWORD` | string | `postgres` | Database Password | No |

---

## Kubernetes Configuration

Configuration is managed via `base/kustomization.yaml`:

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

**Deploy with Kustomize:**
```bash
kubectl apply -k base/ -n biletado
kubectl logs -f deployment/reservations-backend -n biletado
```

---

## API Endpoints

### Health & Status
- `GET /health` - Health Check
- `GET /status` - API Status
- `GET /api/v3/reservations/health` - Service Health
- `GET /api/v3/reservations/status` - Service Status

### Reservations
- `GET /api/v3/reservations/reservations` - Get all reservations
- `GET /api/v3/reservations/reservations/{id}` - Get specific reservation
- `POST /api/v3/reservations/reservations` - Create new reservation
- `PUT /api/v3/reservations/reservations/{id}` - Update or restore reservation
- `DELETE /api/v3/reservations/reservations/{id}` - Delete reservation (soft delete)

**Authentication:** All POST/PUT/DELETE endpoints require a valid JWT token in the `Authorization: Bearer <token>` header

---

## CI/CD Pipeline

The project includes an automated CI/CD pipeline that runs on every push:

**Pipeline Stages:**
- **Code Quality** (pylint, black, flake8)
- **Unit Tests** (pytest + Coverage)
- **Security Scans** (bandit, safety)
- **Docker Image Build**

**View pipeline logs:** Repository → Actions → [Run] → Jobs

---

## Testing

#### Run unit tests (verbose)
```bash
pytest tests/ -v
```

#### Run tests with coverage (HTML + terminal)
```bash
pytest tests/ --cov=app --cov-report=html --cov-report=term
```

#### Run a single test file or test
```bash
pytest tests/test_example.py -q
pytest tests/test_example.py::test_specific_case -q
```

#### Open HTML coverage report
```bash
# After running coverage
# Linux / macOS
xdg-open htmlcov/index.html || open htmlcov/index.html

# Windows (PowerShell)
Start-Process htmlcov\index.html
```

#### Useful options
- `-k "<expr>"` run tests matching expression
- `-x` stop after first failure
- `-m "<marker>"` run tests with a specific marker
- `--maxfail=1` limit failures shown
- `-q` quiet output
- `-s` show print/log output during tests
- `--cov-branch` enable branch coverage (when using coverage)

---

## Logging

**View local logs:**
```bash
uvicorn app.main:app --reload --log-level debug
```

**Change log level:**
```bash
export LOG_LEVEL=DEBUG
python app/main.py
```

**View Kubernetes logs:**
```bash
kubectl logs -f deployment/reservations-backend -n biletado
kubectl logs deployment/reservations-backend -n biletado --tail=50
```

**Log Format:**
All logs contain:
- ISO 8601 Timestamp (UTC)
- Log Level (DEBUG, INFO, WARNING, ERROR)
- Operation (CREATE, READ, UPDATE, DELETE)
- User ID and Object IDs
- JSON format for structured processing

---

## Security

- **JWT authentication** for all sensitive endpoints
- **Token expiration** after configurable duration (default: 30 minutes)
- **Pydantic validation** for all inputs
- **SQLAlchemy ORM** prevents SQL injection
- **Soft-delete** for audit trail

---

## Dependencies

See [requirements.txt](reservations-backend/requirements.txt) for complete list.

---

## License

MIT License - Copyright (c) 2025 jonessy05
