from typing import Any

from fastapi import APIRouter

from app import schemas

router = APIRouter()


@router.get("", response_model=schemas.Msg)
def test_status() -> Any:
    """
    Check status.
    """
    return {"msg": "App is running"}
