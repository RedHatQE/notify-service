from typing import Any

from fastapi import APIRouter

from app import schemas
from app.core.config import settings
from app.utils import irc

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
async def send_message(channel: str, message: str) -> Any:
    if not settings.IRC_SERVER:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="The IRC Server is not configured."
        )
    await irc.send_message(message, channel)

    return {"msg": "Message have been sent"}
