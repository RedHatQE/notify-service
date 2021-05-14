from unittest import mock
from typing import Dict
from httpx import Response

from fastapi.testclient import TestClient

from app.core.config import settings


@mock.patch('httpx.AsyncClient.post', return_value=Response(status_code=200))
def test_chat_default(
        mock_post, client: TestClient, api_key_headers: Dict[str, str]) -> None:
    _target = 'gchat'
    _subject = "TEST"
    params = {
        "target": _target,
        "subject": _subject
    }
    _body = {
        "body": "SAMPLE MESSAGE"
    }
    r = client.post(f"{settings.API_V1_STR}/chat",
                    json=_body,
                    params=params,
                    allow_redirects=True,
                    headers=api_key_headers)
    assert r.status_code == 200
    assert r.text
