import httpx

from typing import Any, Optional, Dict

from fastapi import APIRouter, status, HTTPException
from pydantic.networks import AnyHttpUrl

from app.core.config import settings
from app import utils, schemas

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
async def send_message(
    subject: str = "",
    template_name: str = "chat_default",
    environment: Dict[str, Any] = {"body": ""},
    webhook_url: Optional[AnyHttpUrl] = None,
    template_url: Optional[AnyHttpUrl] = None
) -> Any:
    """
    Send chat message with template

    - **webhook_url**: chat webhook url address, optional
    - **template_name**: template name in local template list, default is "default"
    - **template_url**: template url, optional
    """
    if "project_name" not in environment:
        subject = "*" + settings.PROJECT_NAME + "* " + subject
    else:
        subject = "*" + environment["project_name"] + "* " + subject

    environment["body"] = "\n".join((subject, environment["body"]))

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    data = await utils.get_template(template_name, template_url, '.jinja', environment)


    if webhook_url:
        url = webhook_url
    else:
        url = settings.CHAT_WEBHOOK_URL

    async with httpx.AsyncClient() as client:
        r = await client.post(url, headers=headers, data=data)

    if r.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=r.status_code,
            detail=r.text,
        )

    return {"msg": r.text}
