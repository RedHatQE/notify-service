from typing import Any

from fastapi import APIRouter
from fastapi import Query
from pydantic.networks import EmailStr

from app import schemas
from app.utils.utils import send_test_email

router = APIRouter()


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr = Query(
        ..., description="The test email address, e.g. abc@example.com"
    ),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}
