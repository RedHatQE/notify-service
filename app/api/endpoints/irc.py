from typing import Any

from fastapi import APIRouter

from app import schemas
from app.core.config import settings
from app.utils import irc

from fastapi import status, HTTPException

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
async def send_message(channel: str, message: str) -> Any:
    """
    Send message to irc channel or user

    - **channel**: The irc channel name start with '#' or a user name
    - **message**: The text message
    """
    if not settings.IRC_SERVER:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The IRC Server is not configured."
        )
    try:
        await irc.send_message(message, channel)
    except OSError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{err}")

    return {"msg": "Message have been sent"}
