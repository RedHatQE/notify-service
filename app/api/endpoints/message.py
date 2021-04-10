from typing import Any, Optional, Union
from pydantic.networks import AnyHttpUrl, EmailStr

from fastapi import APIRouter, Query, Body, status, HTTPException

from app import schemas
from app.core.config import settings
from app.api.endpoints import email, chat, irc, message_bus

router = APIRouter()

TARGET = ['email', 'gchat', 'slack', 'irc', 'message_bus']


def param_err(err: str) -> Any:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=err)


@router.post("/", response_model=schemas.Msg)
async def msg_multi_tgts(
    target: str = Query(
        ...,
        description="The message targets seperate by ',', e.g. email,gchat,slack,irc,message_bus"
    ),
    irc_channel: str = Query(
        None,
        description="IRC channel name start with '#' or a user name, e.g. channel #test or user john"
    ),
    email_to: EmailStr = Query(
        None, description="Email address, e.g. abc@example.com"
    ),
    email_template_name: str = Query(
        "default",
        description="The jinja template name without subfix, e.g. default. "
        "Check jinja mjml at: https://github.com/waynesun09/notify-service/blob/main/app/templates/src/"
    ),
    subject: str = Query(
        f"Notification from {settings.PROJECT_NAME}",
        description="The message subject"
    ),
    message_bus_topic: str = Query(
        settings.MSG_DEFAULT_TOPIC,
        description="The message topic or queue value, e.g. /topic/VirtualTopic.qe.ci.test.abc.test.complete"
    ),
    environment: Union[schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody] = Body(
        ...,
        example={
            "body": "SAMPLE PLAIN TEXT MESSAGE OR JSON DICT."
        },
        description="The body values for parse with template or send "
        "Check sample at https://github.com/waynesun09/notify-service/tree/main/docs/sample"
    ),
    gchat_webhook_url: Optional[AnyHttpUrl] = Query(
        settings.GCHAT_WEBHOOK_URL,
        description="The gchat webhook url"
    ),
    slack_webhook_url: Optional[AnyHttpUrl] = Query(
        settings.SLACK_WEBHOOK_URL,
        description="The slack webhook url"
    )
) -> Any:
    """
    Send text messages to multiple supported backends

    - **target**: target backend seperate by ',', e.g. email,gchat,slack,irc,message_bus, required
    - **subject**: message subject, optional
    - **channel**: The irc channel name start with '#' or a user name, optional
    - **email_to**: email address, optional
    - **gchat_webhook_url**: gchat webhook url address, optional
    - **slack_webhook_url**: slack webhook url address, optional
    """
    target = [i.strip() for i in target.split(',')]
    for t in target:
        if t not in TARGET:
            detail = f"The target {t} is not supported"
            param_err(detail)

    if (("gchat" in target and not gchat_webhook_url) or
            ("slack" in target and not slack_webhook_url)):
        detail = "The chat webhook url have not been provided"
        param_err(detail)

    if 'irc' in target and not irc_channel:
        detail = "The IRC channel have not been provided"
        param_err(detail)

    if "email" in target and not email_to:
        detail = "The email address have not been provided"
        param_err(detail)

    if 'message_bus' in target and not message_bus_topic:
        detail = "The message bus topic have not been provided"
        param_err(detail)

    body = environment.body
    env = environment.copy()

    if 'gchat' in target:
        await chat.send_message(
            'gchat',
            subject=subject,
            environment=environment,
            template_name="chat_default",
            webhook_url=gchat_webhook_url,
            template_url=None
        )

    if 'slack' in target:
        await chat.send_message(
            'slack',
            subject=subject,
            environment=environment,
            template_name="chat_default",
            webhook_url=slack_webhook_url,
            template_url=None
        )

    if 'irc' in target:
        # Only text is supported, so convert body to str
        text = "{}:\n{}".format(subject, str(environment.body))
        await irc.send_message(
            channel=irc_channel,
            message=text
        )

    if 'email' in target:
        await email.send_email(
            email_to,
            subject=subject,
            template_name=email_template_name,
            environment=environment,
            template_url=None
        )

    # Use environment copy as message bus backend could parse both random dict and text
    if 'message_bus' in target:
        message_bus.send_message(
            topic=message_bus_topic,
            environment=env
        )

    return {"msg": f"Message have been send to all targets {target}"}
