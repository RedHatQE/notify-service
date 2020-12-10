import os
import shutil

from pathlib import Path

from typing import Any

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.core.config import settings
from app.utils import get_file_path, read_file

router = APIRouter()


@router.get("/")
def get_template_list() -> Any:
    """
    Get template list
    """
    default = os.listdir(settings.EMAIL_TEMPLATES_DIR)
    extra = []
    if settings.TEMPLATE_MOUNT_DIR:
        extra = os.listdir(settings.TEMPLATE_MOUNT_DIR)
    return {"default": default, "customized": extra}


@router.get("/{tmplt_name}")
def get_template(tmplt_name: str) -> Any:
    """
    Get template content with tmplate name without postfix
    """
    file_path = get_file_path(settings.TEMPLATE_MOUNT_DIR, tmplt_name)
    if file_path:
        return {tmplt_name: read_file(file_path)}

    file_path = get_file_path(settings.EMAIL_TEMPLATES_DIR, tmplt_name)
    if file_path:
        return {tmplt_name: read_file(file_path)}

    raise HTTPException(
        status_code=400,
        detail="The given template name does not exist")


@router.put("/{tmplt_name}")
def update_template(tmplt_name: str, tmplt: UploadFile = File(...)) -> Any:
    """
    Create or update a template under template mount dir
    """
    destination = Path(settings.TEMPLATE_MOUNT_DIR).joinpath(tmplt_name + '.html')
    try:
        with destination.open("wb") as f:
            shutil.copyfileobj(tmplt.file, f)
    finally:
        tmplt.file.close()
    return {tmplt_name: tmplt}
