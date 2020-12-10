import requests
import jinja2

from typing import Any, Optional, Dict

from fastapi import APIRouter, HTTPException
from pydantic.networks import AnyHttpUrl, EmailStr

from app.core.config import settings
from app import utils, schemas

router = APIRouter()


@router.post("/", response_model=schemas.Msg)
def send_email(
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

    if template_url:
        r = requests.get(template_url)
        r.raise_for_status()
        template = r.text
    else:
        template_dir = [settings.EMAIL_TEMPLATES_DIR]
        if settings.TEMPLATE_MOUNT_DIR:
            template_dir.append(settings.TEMPLATE_MOUNT_DIR)
        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir))
        template = jinja_env.get_template(template_name + '.html').render(environment)
        environment = {}

    if not template:
        raise HTTPException(
            status_code=400,
            detail="The given template is empty")

    utils.send_email(
            email_to=email_to, subject_template=subject,
            html_template=template, environment=environment)

    return {"msg": "Email have been sent"}
