from unittest import mock
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings

@mock.patch('app.utils.message_bus.quick_send')
def test_message_bus_default(
        mock_send, client: TestClient, api_key_headers: Dict[str, str]) -> None:
    _topic = "test"
    params = {
        "topic": _topic
    }
    _body = {
        "body": "SAMPLE MESSAGE"
    }
    r = client.post(f"{settings.API_V1_STR}/message_bus",
                    json=_body,
                    params=params,
                    allow_redirects=True,
                    headers=api_key_headers)
    assert r.status_code == 200
    assert r.text == '{"msg":"Message have been sent"}'
