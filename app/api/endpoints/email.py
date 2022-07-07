from typing import Any, List, Optional, Union

from fastapi import APIRouter, Query, Body
from pydantic.networks import AnyHttpUrl, EmailStr

from app import schemas
from app.utils import utils
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
async def send_email(
    email_to: List[EmailStr] = Query(
        ..., description="Email address, e.g. abc@example.com"
    ),
    subject: str = Query("", description="The email subject"),
    template_name: str = Query(
        "default",
        description="The jinja html template name without subfix, e.g. default. "
        "Check jinja mjml at: https://github.com/RedHatQE/notify-service/blob/main/app/templates/src/"
    ),
    environment: Union[
        schemas.DictBody,
        schemas.TxtBody,
        schemas.EmailResult,
        schemas.BaseResultBody
    ] = Body(
        ...,
        example={
            "body": "SAMPLE MESSAGE"
        },
        description="The body values for parse with the template. "
        "Check samples at: https://github.com/RedHatQE/notify-service/tree/main/docs/sample"
    ),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the template_name if given"
    )
) -> Any:
    """
    Send email with template

    - **email_to**: email address, required
    - **subject**: email subject, optional
    - **template_name**: template name in local template list, default is "default"
    - **template_url**: template url, optional
    - **Request Body**: Check samples at https://github.com/RedHatQE/notify-service/tree/main/docs/sample
    """
    env = {}
    if (not template_url and
            (isinstance(environment.body, str) or
                (template_name == 'default' and "body" not in environment.body))):
        # Set 'body' in env dict, this will work with default template
        env["body"] = environment.body
    else:
        # Pass the body dict value to the env dict, it will be parsed by specific template
        env = environment.body

    if environment.project_name:
        env["project_name"] = environment.project_name
    else:
        env["project_name"] = settings.PROJECT_NAME

    data = await utils.get_template(template_name, template_url, '.html', env)

    utils.send_email(
        email_to=email_to, subject_template=subject,
        html_template=data, environment={})

    return {"msg": "Email have been sent"}
