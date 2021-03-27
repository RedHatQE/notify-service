from typing import Any

from fastapi import APIRouter, Query

from app import schemas
from app.core.config import settings
from app.utils import irc

from fastapi import status, HTTPException

router = APIRouter()


async def _send_message(message, channel) -> Any:
    """
    Call irc send_message
    """
    try:
        await irc.send_message(message, channel)
    except OSError as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{err}. Please check IRC config is right and server:port is accessible.")


@router.post("/", response_model=schemas.Msg)
async def send_message(
    channel: str = Query(
        ...,
        description="IRC channel name start with '#' or a user name, e.g. channel #test or user john"),
    message: str = Query(None, description="The text message")
) -> Any:
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
    # Avoid text limit for 512 bytes, split message with length greater than 450
    if len(message) > 420:
        n = 420
        chunks = [message[i:i + n] for i in range(0, len(message), n)]
        for i in chunks:
            await _send_message(i, channel)
    else:
        await _send_message(message, channel)

    return {"msg": "Message have been sent"}
