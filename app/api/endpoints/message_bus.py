import json

from typing import Any, Dict

from fastapi import APIRouter, status, HTTPException

from app import schemas
from app.utils import message_bus
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
def send_message(
        topic: str,
        environment: Dict[str, Any] = {"headers": {}, "body": {}}
) -> Any:
    if not settings.MSG_BUS_HOST_1 and not settings.MSG_BUS_HOST_2:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="None MSG_BUS_HOST is configured."
        )
    headers = environment["headers"]
    body = json.dumps(environment["body"], indent=4)
    message_bus.quick_send(topic, headers, body)

    return {"msg": "Message have been sent"}
