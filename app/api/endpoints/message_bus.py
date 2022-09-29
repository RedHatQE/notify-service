import json
from typing import Any
from typing import Union

from fastapi import APIRouter
from fastapi import Body
from fastapi import HTTPException
from fastapi import Query
from fastapi import status

from app import schemas
from app.core.config import settings
from app.utils import message_bus

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
def send_message(
    topic: str = Query(
        settings.MSG_DEFAULT_TOPIC,
        description="The message topic or queue value, "
        "e.g. /topic/VirtualTopic.qe.ci.test.abc.test.complete",
    ),
    environment: Union[schemas.TxtBody, schemas.DictBody] = Body(
        ...,
        example={
            "headers": {"CI_NAME": "EXAMPLE", "CI_TYPE": "CUSTOM"},
            "body": message_bus.MESSAGE_BODY_EXAMPLE,
        },
        description="The message body with message headers and body value. "
        "Check fedora-ci message samples at: https://pagure.io/fedora-ci/messages/blob/master/f/examples/",
    ),
) -> Any:
    if not settings.MSG_BUS_HOST_1 and not settings.MSG_BUS_HOST_2:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="None MSG_BUS_HOST is configured.",
        )
    headers = None
    if hasattr(environment, "headers"):
        headers = environment.headers
    body = json.dumps(environment.body, indent=4)
    message_bus.quick_send(topic, headers, body)

    return {"msg": "Message have been sent"}
