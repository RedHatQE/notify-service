from fastapi import HTTPException
from fastapi import Security
from fastapi import status
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings

API_KEY = settings.SECRET_KEY
API_KEY_NAME = "X-API-KEY"

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
