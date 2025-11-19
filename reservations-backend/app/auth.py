"""
JWT-Verifikation und Authentifizierung
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
import os
import logging

logger = logging.getLogger(__name__)

# Konfiguration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
JWT_ISSUER_URL = os.getenv("JWT_ISSUER_URL", None)
DISABLE_AUTH = os.getenv("DISABLE_AUTH", "false").lower() == "true"

security = HTTPBearer(auto_error=not DISABLE_AUTH)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Erstellt einen JWT Access Token
    
    Args:
        data: Daten die im Token codiert werden (z.B. {"sub": "user_id"})
        expires_delta: Ablaufzeit (optional)
    
    Returns:
        Codierter JWT Token als String
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.debug(f"Created token for user: {data.get('sub')}")
    return encoded_jwt


async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> str:
    """
    Verifiziert einen JWT Token (lokal oder über Keycloak)
    
    Args:
        credentials: HTTP Bearer Token
    
    Returns:
        Benutzer-ID (subject) aus dem Token
    
    Raises:
        HTTPException: Wenn Token ungültig oder abgelaufen ist
    """
    # Auth disabled for development/testing
    if DISABLE_AUTH:
        logger.warning("Authentication is DISABLED - using anonymous user")
        return "anonymous"
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = credentials.credentials
    
    # Nutze Keycloak wenn konfiguriert
    if JWT_ISSUER_URL:
        try:
            from app.keycloak_auth import validate_token_with_keycloak
            payload = validate_token_with_keycloak(token)
            user_id = payload.get("sub") or payload.get("preferred_username")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: no subject found",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            logger.debug(f"Token validated via Keycloak for user: {user_id}")
            return user_id
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Keycloak validation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    # Fallback: lokale Validierung mit SECRET_KEY
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.debug(f"Token validated locally for user: {user_id}")
        return user_id
    
    except JWTError:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
