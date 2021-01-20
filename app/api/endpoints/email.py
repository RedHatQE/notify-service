from typing import Any, Optional, Dict

from fastapi import APIRouter
from pydantic.networks import AnyHttpUrl, EmailStr

from app import schemas
from app.utils import utils
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
async def send_email(
    email_to: EmailStr,
    subject: str = "",
    template_name: str = "default",
    environment: Dict[str, Any] = {"body": {}},
    template_url: Optional[AnyHttpUrl] = None
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
