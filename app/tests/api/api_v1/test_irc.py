from typing import Dict
from unittest import mock

from fastapi.testclient import TestClient

from app.core.config import settings


@mock.patch("app.utils.irc.send_message")
def test_irc_default(
    mock_send, client: TestClient, api_key_headers: Dict[str, str]
) -> None:
    _channel = "test"
    _message = "TEST"
    params = {"channel": _channel, "message": _message}
    r = client.post(
        f"{settings.API_V1_STR}/irc",
        params=params,
        allow_redirects=True,
        headers=api_key_headers,
    )
    assert r.status_code == 200
    assert r.text
