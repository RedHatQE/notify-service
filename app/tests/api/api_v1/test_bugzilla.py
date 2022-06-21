from unittest import mock
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings

@mock.patch('bugzilla.Bugzilla.createbug')
def test_bugzilla_new_bug(
        mock_post, client: TestClient, api_key_headers: Dict[str, str]) -> None:
    params = {
        "product": "Fedora",
        "version": "rawhide",
        "component": "python-bugzilla",
        "summary": "Test"
    }
    _body = {
        "body": "SAMPLE MESSAGE"
    }

    r = client.post(f"{settings.API_V1_STR}/bugzilla/new_bugzilla_bug",
                    json=_body,
                    params=params,
                    allow_redirects=True,
                    headers=api_key_headers)

    assert r.status_code == 200


@mock.patch('bugzilla.Bugzilla.update_bugs')
def test_bugzilla_new_comment(
        mock_post, client: TestClient, api_key_headers: Dict[str, str]) -> None:
    params = {
        "bug_id": "12345"
    }
    _body = {
        "body": "SAMPLE MESSAGE"
    }

    r = client.post(f"{settings.API_V1_STR}/bugzilla/new_bugzilla_comment",
                    json=_body,
                    params=params,
                    allow_redirects=True,
                    headers=api_key_headers)

    assert r.status_code == 200
