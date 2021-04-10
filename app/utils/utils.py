import aiofile
import emails
import httpx
import logging
import os
import json
import subprocess
import uuid

from datetime import datetime, timedelta
from emails.template import JinjaTemplate
from fastapi_cache.decorator import cache
from fastapi import HTTPException
from jose import jwt
from jinja2 import BaseLoader, Environment, FileSystemLoader
from pathlib import Path
from pydantic.networks import AnyHttpUrl
from typing import Any, Dict, Optional

from app.core.config import settings


@cache(expire=300)
async def request_get_text(url: AnyHttpUrl):
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.get(url)
        return r.text


def add_examples(openapi_schema: dict) -> dict:
    """
    Generate openapi schema with x-code-samples by snippet-enricher-cli command
    """
    lans = "shell_curl,python_python3,go_native,java_unirest,node_native,javascript_xhr"
    uid = str(uuid.uuid4())[:8]
    tmp_json = Path(f"{settings.TEMPLATE_MOUNT_DIR}/openapi_{uid}.json")
    example_json = Path(f"{settings.TEMPLATE_MOUNT_DIR}/openapi_{uid}_example.json")
    try:
        if tmp_json.is_file():
            tmp_json.unlink()

        with open(tmp_json, 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f)

        cmd = f"snippet-enricher-cli --targets='{lans}' --input={tmp_json} > {example_json}"
        subprocess.run(cmd, shell=True, check=True)

        with open(example_json, 'r', encoding='utf-8') as f:
            return json.load(f)
    finally:
        if tmp_json.is_file():
            tmp_json.unlink()
        if example_json.is_file():
            example_json.unlink()


def get_file_path(path_name: str, tmplt_name: str) -> str:
    """
    Check file exist and return file path
    """
    for root, _, files in os.walk(path_name, topdown=False):
        file_list = [i.split(".")[0] for i in files]
        if tmplt_name in file_list:
            return os.path.join(root, files[file_list.index(tmplt_name)])
    return None


async def get_template(name: str, url: Optional[AnyHttpUrl] = None,
                       suffix: str = '.html', env: Optional[Dict] = None) -> str:
    """
    Get template from http url or local file and render
    """
    if url:
        r = await request_get_text(url=url)
        template = Environment(loader=BaseLoader()).from_string(r).render(env)
    else:
        template_dir = [settings.EMAIL_TEMPLATES_DIR]
        if settings.TEMPLATE_MOUNT_DIR:
            template_dir.append(settings.TEMPLATE_MOUNT_DIR)
        jinja_env = Environment(
            loader=FileSystemLoader(template_dir))
        try:
            template = jinja_env.get_template(name + suffix).render(env)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"{e}")

    if not template:
        raise HTTPException(
            status_code=400,
            detail="The given template is empty")

    return template


@cache(expire=5)
async def read_file(path_name: str) -> str:
    """
    Read file with given path
    """
    async with aiofile.async_open(path_name, 'r') as f:
        tmplt = await f.read()
    return tmplt


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variables"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email}, settings.SECRET_KEY, algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.JWTError:
        return None
