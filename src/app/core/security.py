import logging
import secrets
from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False,
    description="API key for authentication. Get your API key from the administrator."
)


def get_api_key(api_key: Optional[str] = Security(api_key_header)) -> str:
    """
    Validate API key from X-API-Key header.
    
    This function extracts the API key from the X-API-Key header and validates it
    against the configured API key in settings. Uses constant-time comparison to
    prevent timing attacks. Works with Swagger UI authentication.
    """
    if not api_key:
        logger.warning("API key authentication failed: Missing API key header")
        raise HTTPException(
            status_code=401,
            detail="API key is required. Please provide X-API-Key header."
        )
    # Strip whitespace in case Swagger UI adds any
    api_key = api_key.strip()
    # Use constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(api_key, settings.API_KEY):
        logger.warning("API key authentication failed: Invalid API key provided")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key. Could not validate API key."
        )
    return api_key
