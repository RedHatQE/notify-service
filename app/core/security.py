from fastapi import Security, status, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "1234567asdfgh"
API_KEY_NAME = "X-API-KEY"

api_key_header_auth = APIKeyHeader(name=API_KEY_NAME, auto_error=True)


async def get_api_key(api_key_header: str = Security(api_key_header_auth)):
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
