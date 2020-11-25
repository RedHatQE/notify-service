import os
import shutil

from pathlib import Path

from typing import Any

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.core.config import settings
from app import schemas

router = APIRouter()


@router.get("/")
def get_template_list() -> Any:
    """
    Get template list
    """
    tmplt_list = os.listdir(settings.EMAIL_TEMPLATES_DIR)
    if settings.TEMPLATE_MOUNT_DIR:
        tmplt_list.append(os.listdir(settings.TEMPLATE_MOUNT_DIR))
    return {"filenames": tmplt_list}


def get_file_path(path_name: str, tmplt_name: str) -> str:
    """
    Check file exist and return file path
    """
    for root, _, files in os.walk(path_name, topdown=False):
        file_list = [i.split(".")[0] for i in files]
        if tmplt_name in file_list:
            return os.path.join(root, files[file_list.index(tmplt_name)])
    return None


def read_file(path_name: str) -> str:
    """
    Read file with given path
    """
    with open(path_name) as f:
        tmplt = f.read()
    return tmplt


@router.get("/{tmplt_name}")
def get_template() -> Any:
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
def update_template(tmplt: UploadFile = File(...)) -> Any:
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
