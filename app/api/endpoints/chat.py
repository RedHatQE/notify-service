import httpx

from typing import Any, Optional, Union

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
        description="The message target, 'gchat' or 'slack'"
    ),
    subject: str = Query("", description="The message subject"),
    template_name: str = Query(
        "chat_default",
        description="The jinja template name without suffix, e.g. chat_default, default to 'chat_default' for gchat. "
        "Check sample at https://github.com/waynesun09/notify-service/tree/main/app/templates/build"
    ),
    environment: Union[schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody] = Body(
        ...,
        example={
            "body": "SAMPLE MESSAGE."
        },
        description="The body values for parse with the template, "
        "check samples at https://github.com/waynesun09/notify-service/tree/main/docs/sample"
    ),
    webhook_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The gchat or slack webhook url"
    ),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote template url, it will override the template_name if given"
    )
) -> Any:
    """
    Send chat message with template

    - **subject**: chat message subject
    - **target**: target chat app, gchat or slack, optional, default is "gchat"
    - **webhook_url**: chat webhook url address, optional
    - **template_name**: template name in local template list, default is "default"
    - **template_url**: template url, optional
    - **Request Body**: Check samples at https://github.com/waynesun09/notify-service/tree/main/docs/sample
    """
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

    env = {}
    # Concatenate project name and subject
    if environment.project_name:
        subject = f"[{environment.project_name}] {subject}"
    else:
        subject = f"[{settings.PROJECT_NAME}] {subject}"

    chunks = []
    n = 4095
    if (isinstance(environment.body, str) or
            (template_name == "chat_default" and isinstance(environment.body, dict)
                and not hasattr(environment.body, "body"))):
        # Pure text message, put the subject into body and add new line
        # Set 'body' value in env dict, this will work with chat default template
        text = "\n".join((subject, str(environment.body)))
        # Gchat webhook 4096 characters limitation
        if target.upper() == "GCHAT" and len(text) > 4095:
            chunks = [text[i:i + n] for i in range(0, len(text), n)]
        else:
            env["body"] = text
    else:
        # Pass the body dict value to the env dict, it will be parsed by specific template
        # Can't split data with parsed jinja template, return client the GChat error if
        # the parsed jinja template character is greater than 4095
        env = environment.body
        env["subject"] = subject

    headers = {'Content-Type': 'application/json; charset=UTF-8'}
    data_list = []
    # Process chunks to text data list
    if chunks:
        for i in chunks:
            env["body"] = str(i)
            data = await utils.get_template(template_name, template_url, '.jinja', env)
            data_list.append(data)
    else:
        data = await utils.get_template(template_name, template_url, '.jinja', env)
        data_list.append(data)

    async with httpx.AsyncClient() as client:
        for i in data_list:
            r = await client.post(url, headers=headers, data=i)
            if r.status_code != status.HTTP_200_OK:
                raise HTTPException(
                    status_code=r.status_code,
                    detail=r.text,
                )

    return {"msg": r.text}
