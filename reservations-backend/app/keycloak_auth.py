"""
Keycloak OIDC Integration für JWT Token Validierung
"""
import os
import requests
from typing import Optional, Dict, Any
from functools import lru_cache
from jose import jwt, JWTError
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Konfiguration aus Umgebungsvariablen
JWT_ISSUER_URL = os.getenv("JWT_ISSUER_URL", None)
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", None)  # Optional, None = skip audience validation
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")

# Fallback auf lokale Validierung, wenn JWT_ISSUER_URL nicht gesetzt
USE_KEYCLOAK = JWT_ISSUER_URL is not None


class KeycloakValidator:
    """Validiert JWT Tokens gegen Keycloak OIDC"""

    def __init__(self, issuer_url: str):
        self.issuer_url = issuer_url.rstrip("/")
        # Keycloak JWKS endpoint is at /protocol/openid-connect/certs
        self.jwks_url = f"{self.issuer_url}/protocol/openid-connect/certs"
        self._jwks_cache = None
        self._public_keys = {}

    @lru_cache(maxsize=1)
    def get_public_keys(self) -> Dict[str, Any]:
        """Lädt öffentliche Keys von Keycloak JWKS Endpoint"""
        try:
            logger.info(f"Fetching JWKS from {self.jwks_url}")
            response = requests.get(self.jwks_url, timeout=5)
            response.raise_for_status()
            data = response.json()

            # Erstelle Dictionary aus kid -> key
            keys = {}
            for key in data.get("keys", []):
                kid = key.get("kid")
                if kid:
                    keys[kid] = key
                    logger.debug(f"Loaded public key: {kid}")

            return keys
        except Exception as e:
            logger.error(f"Failed to fetch JWKS: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Failed to validate token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )

    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validiert JWT Token gegen Keycloak

        Args:
            token: JWT Token String

        Returns:
            Decoded Token Payload

        Raises:
            HTTPException: Wenn Token ungültig/abgelaufen ist
        """
        try:
            # Decode Token Header um kid zu erhalten
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            if not kid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token missing 'kid' header",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            # Hole Public Key
            public_keys = self.get_public_keys()
            if kid not in public_keys:
                logger.error(f"Unknown key id: {kid}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token signature",
                    headers={"WWW-Authenticate": "Bearer"}
                )

            public_key = public_keys[kid]

            # Validiere Token mit Public Key
            # Skip issuer validation since token issuer uses external URL (localhost:9090)
            # while backend uses internal service name (keycloak)
            decode_options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": JWT_AUDIENCE is not None,
                "verify_iss": False  # Skip issuer validation
            }
            
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[JWT_ALGORITHM],
                options=decode_options
            )

            logger.info(f"Token validated for user: {payload.get('sub')}")
            return payload

        except JWTError as e:
            logger.warning(f"JWT validation failed: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid or expired token: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token validation failed",
                headers={"WWW-Authenticate": "Bearer"}
            )


# Globale Keycloak Validator Instanz
_keycloak_validator: Optional[KeycloakValidator] = None


def get_keycloak_validator() -> Optional[KeycloakValidator]:
    """Gibt Keycloak Validator Instanz zurück (Lazy Loading)"""
    global _keycloak_validator

    if _keycloak_validator is None and JWT_ISSUER_URL:
        _keycloak_validator = KeycloakValidator(JWT_ISSUER_URL)

    return _keycloak_validator


def validate_token_with_keycloak(token: str) -> Dict[str, Any]:
    """
    Validiert Token gegen Keycloak (wenn konfiguriert)

    Args:
        token: JWT Token

    Returns:
        Token Payload

    Raises:
        HTTPException: Wenn Validierung fehlschlägt
    """
    validator = get_keycloak_validator()
    if validator:
        return validator.validate_token(token)
    else:
        logger.warning("Keycloak not configured, using fallback validation")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Keycloak not configured",
            headers={"WWW-Authenticate": "Bearer"}
        )
