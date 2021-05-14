import uuid

from http import HTTPStatus
from pathlib import Path
from typing import Dict
from unittest import mock

from fastapi.testclient import TestClient

from app.core.config import settings


def test_get_template_list(
        client: TestClient, api_key_headers: Dict[str, str]) -> None:
    r = client.get(f"{settings.API_V1_STR}/template", headers=api_key_headers)
    tmplt = r.json()
    assert tmplt
    assert "default" in tmplt
    assert "customized" in tmplt


@mock.patch('app.utils.utils.read_file')
def test_get_template(
        client: TestClient, api_key_headers: Dict[str, str]) -> None:
    _file_name = "default"
    r = client.get(f"{settings.API_V1_STR}/template/{_file_name}",
                   headers=api_key_headers)
    tmplt = r.json()
    assert tmplt


def test_update_template(
        client: TestClient, api_key_headers: Dict[str, str]) -> None:
    _file_name = "default_" + str(uuid.uuid1())[:8]
    _test_upload_file = Path(settings.EMAIL_TEMPLATES_DIR, 'default.html')
    try:
        _files = {'tmplt': _test_upload_file.open('rb')}
        r = client.put(f"{settings.API_V1_STR}/template/{_file_name}",
                       files=_files, headers=api_key_headers)
        assert r.status_code == HTTPStatus.OK
        assert _file_name in r.json()
    finally:
        _copied_file = Path(settings.TEMPLATE_MOUNT_DIR, _file_name + ".html")
        _copied_file.unlink()
