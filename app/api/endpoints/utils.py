from typing import Any

from fastapi import APIRouter
from pydantic.networks import EmailStr

from app import schemas
from app.utils.utils import send_test_email

router = APIRouter()


@router.get("/status", response_model=schemas.Msg)
def test_status() -> Any:
    """
    Check status.
    """
    return {"msg": "App is running"}


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}
