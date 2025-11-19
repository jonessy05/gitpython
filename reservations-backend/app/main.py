"""
Einstiegspunkt - FastAPI Application mit Routes
"""
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from datetime import datetime, timedelta, timezone
from app.routes import reservations
from app.auth import create_access_token
from app.logging_config import logger
import os

# Logging initialisieren
logger.info("Starting Reservierungen API", extra={
    "operation": "STARTUP",
    "user_id": "system",
    "object_type": "api",
    "object_id": "reservations-api"
})

# Konfiguration aus Umgebungsvariablen anzeigen
jwt_issuer = os.getenv("JWT_ISSUER_URL", "Not configured")
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.info(f"Configuration: JWT_ISSUER_URL={jwt_issuer}, LOG_LEVEL={log_level}", extra={
    "operation": "CONFIG",
    "user_id": "system",
    "object_type": "config",
    "object_id": "api-config"
})

# FastAPI Instanz erstellen
app = FastAPI(
    title="Reservierungen API",
    description="API für die Verwaltung von Reservierungen mit JWT-Authentifizierung",
    version="1.0.0",
)

# Routes registrieren
app.include_router(reservations.router)


@app.get("/health", tags=["system"], status_code=status.HTTP_200_OK)
def health_check() -> dict:
    """
    Health Check Endpoint
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/status", tags=["system"], status_code=status.HTTP_200_OK)
def api_status() -> dict:
    """
    API Status Endpoint with authors information
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "api": "Reservierungen API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authors": [
            {
                "name": "Jonas",
                "role": "Developer"
            }
        ]
    }


@app.get("/api/v3/reservations/status", tags=["status"], status_code=status.HTTP_200_OK)
def api_v3_reservations_status() -> dict:
    """
    API v3 Status Endpoint - information about the API-Status
    """
    return {
        "status": "ok",
        "version": "1.0.0",
        "api": "biletado/reservations-v3",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "authors": [
            "Jonas"
        ]
    }


@app.get("/api/v3/reservations/health", tags=["status"], status_code=status.HTTP_200_OK)
def api_v3_reservations_health() -> dict:
    """
    Health information about the service
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/v3/reservations/health/live", tags=["status"], status_code=status.HTTP_200_OK)
def api_v3_reservations_health_live() -> dict:
    """
    Liveness information about the service. Can be used for liveness probes.
    """
    return {
        "status": "alive",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/api/v3/reservations/health/ready", tags=["status"], status_code=status.HTTP_200_OK)
def api_v3_reservations_health_ready() -> dict:
    """
    Readiness information about the service. Can be used for readiness probes.
    """
    # Check if database is initialized
    from app.database import _reservations_db
    is_ready = len(_reservations_db) > 0
    
    if not is_ready:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "not ready",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    
    return {
        "status": "ready",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.post("/auth/token", tags=["authentication"])
def login(username: str) -> dict:
    """
    Test-Authentifizierung: Generiert einen JWT Token
    
    **Hinweis:** Dies ist nur für Testzwecke. In der Produktion sollte 
    eine echte Authentifizierung mit Passwort-Verifikation implementiert werden.
    """
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Test token generated for user: {username}", extra={
        "operation": "AUTH",
        "user_id": username,
        "object_type": "token",
        "object_id": "test-token"
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60  # Sekunden
    }


@app.get("/auth/token", tags=["authentication"])
def get_token(username: str = "testuser") -> dict:
    """
    Test-Token per GET generieren (einfach für Tests)
    
    Beispiel: /auth/token?username=jonas
    """
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": username},
        expires_delta=access_token_expires
    )
    
    logger.info(f"Test token generated for user: {username}", extra={
        "operation": "AUTH",
        "user_id": username,
        "object_type": "token",
        "object_id": "test-token"
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,
        "usage": "Add this to Authorization header: Bearer " + access_token
    }


@app.get("/", tags=["root"])
def read_root() -> dict:
    """
    Root Endpoint mit Willkommensnachricht
    """
    return {
        "message": "Willkommen bei der Reservierungen API",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "auth_token": "/auth/token",
            "status": "/api/v3/status",
            "reservations": "/api/v3/reservations"
        }
    }


# Optionale OpenAPI Schema Anpassung
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Reservierungen API",
        version="1.0.0",
        description="API für die Verwaltung von Reservierungen mit JWT-Authentifizierung",
        routes=app.routes,
    )
    
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi