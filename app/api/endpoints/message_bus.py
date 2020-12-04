from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_message_bus_setting() -> Any:
    pass
