from typing import Dict
from unittest import mock

from fastapi.testclient import TestClient

from app.core.config import settings


@mock.patch("emails.message.Message.send")
def test_send_email_default(
    mock_send, client: TestClient, api_key_headers: Dict[str, str]
) -> None:
    _email_to = "abc@example.com"
    _subject = "TEST"
    params = {"email_to": _email_to, "subject": _subject}
    _body = {"body": "SAMPLE MESSAGE"}
    r = client.post(
        f"{settings.API_V1_STR}/email",
        json=_body,
        params=params,
        allow_redirects=True,
        headers=api_key_headers,
    )
    assert r.status_code == 200
    assert r.text == '{"msg":"Email have been sent"}'
