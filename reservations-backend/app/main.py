"""
Einstiegspunkt - FastAPI Application mit Routes
"""
from fastapi import FastAPI, status
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
            "reservations": "/reservations"
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