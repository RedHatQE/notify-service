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
            detail=f"{err}. Please check IRC config is right and server:port is accessible."
        )


@router.post("/", response_model=schemas.Msg)
async def send_message(
    channel: str = Query(
        ...,
        description="IRC channel name start with '#' or a user name, e.g. channel #test or user john"
    ),
    message: str = Query(
        ...,
        description="The text message",
        example="SAMPLE MESSAGE"
    )
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
    lines = await irc.process_lines(message)
    for line in lines:
        await _send_message(line, channel)

    return {"msg": "Message have been sent"}
