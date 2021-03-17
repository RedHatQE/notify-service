from typing import Any, Optional, Dict

from fastapi import APIRouter, Query, Body
from pydantic.networks import AnyHttpUrl, EmailStr

from app import schemas
from app.utils import utils
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
async def send_email(
    email_to: EmailStr = Query(..., description="Email address, e.g. abc@example.com"),
    subject: str = Query("", description="The email subject"),
    template_name: str = Query("default", description="The template name without subfix, e.g. default"),
    environment: Dict[str, Any] = Body({"body": {}}, description="The body values for parse with the template"),
    template_url: Optional[AnyHttpUrl] = Query(None, description="The remote teamplate url, it will overide the template_name if given")
) -> Any:
    """
    Send email with template

    - **email_to**: email address, required
    - **template_name**: template name in local template list, default is "default"
    - **template_url**: template url, optional
    """
    if "project_name" not in environment:
        environment["project_name"] = settings.PROJECT_NAME

    data = await utils.get_template(template_name, template_url, '.html', environment)

    utils.send_email(
        email_to=email_to, subject_template=subject,
        html_template=data, environment={})

    return {"msg": "Email have been sent"}
