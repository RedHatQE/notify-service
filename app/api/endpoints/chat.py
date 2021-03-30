import httpx

from typing import Any, Optional, Dict

from fastapi import APIRouter, Query, Body, status, HTTPException
from pydantic.networks import AnyHttpUrl

from app import schemas
from app.utils import utils
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
async def send_message(
    target: str = Query(
        ...,
        description="The message target, 'gchat' or 'slack'"),
    subject: str = Query("", description="The message subject"),
    template_name: str = Query(
        "chat_default",
        description="The template name without suffix, e.g. chat_default, default to 'chat_default' for gchat"),
    environment: Dict[str, Any] = Body(
        {"body": ""},
        description="The body values for parse with the template"),
    webhook_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The gchat or slack webhook url"),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote template url, it will overide the template_name if given")
) -> Any:
    """
    Send chat message with template

    - **subject**: chat message subject
    - **target**: target chat app, gchat or slack, optional, default is "gchat"
    - **webhook_url**: chat webhook url address, optional
    - **template_name**: template name in local template list, default is "default"
    - **template_url**: template url, optional
    """
    if "project_name" not in environment:
        subject = " ".join((settings.PROJECT_NAME, subject))
    else:
        subject = " ".join((environment["project_name"], subject))

    if "body" in environment and isinstance(environment["body"], str):
        environment["body"] = "\n".join((subject, environment["body"]))
    else:
        environment["subject"] = subject

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    data = await utils.get_template(template_name, template_url, '.jinja', environment)


    if webhook_url:
        url = webhook_url
    elif target.upper() == "GCHAT":
        url = settings.GCHAT_WEBHOOK_URL
    elif target.upper() == "SLACK":
        url = settings.SLACK_WEBHOOK_URL
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="webhook_url, GCHAT_WEBHOOK_URL or SLACK_WEBHOOK_URL is not provided."
        )

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, data=data)

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=r.status_code,
            detail=r.text,
        )

    return {"msg": r.text}
