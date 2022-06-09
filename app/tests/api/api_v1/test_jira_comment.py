from unittest import mock
from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings

options = {'server': settings.JIRA_URL}

@mock.patch('jira.JIRA.add_comment')
def test_jira_comment_default(
        mock_post, client: TestClient, api_key_headers: Dict[str, str]) -> None:
    _comment_key = 'JRA-9'
    params = {
        "comment_key": _comment_key
    }
    _body = {
        "body": "SAMPLE MESSAGE"
    }
    api_key_headers.update({"url": settings.JIRA_URL})


    r = client.post(f"{settings.API_V1_STR}/jira_add_comment",
                    json=_body,
                    params=params,
                    allow_redirects=True,
                    headers=api_key_headers)

    assert r.status_code == 200
