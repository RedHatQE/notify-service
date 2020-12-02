from typing import Any

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def get_sms_setting() -> Any:
    pass
