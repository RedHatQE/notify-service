from typing import Dict
from unittest import mock

from fastapi.testclient import TestClient

from app.core.config import settings


@mock.patch("jira.JIRA.add_comment")
def test_jira_comment_default(
    mock_post, client: TestClient, api_key_headers: Dict[str, str]
) -> None:
    _issue_key = "JRA-9"
    params = {"issue_key": _issue_key}
    _body = {"body": "SAMPLE MESSAGE"}
    api_key_headers.update({"url": "https://jira.atlassian.com"})

    r = client.post(
        f"{settings.API_V1_STR}/jira/add_comment",
        json=_body,
        params=params,
        allow_redirects=True,
        headers=api_key_headers,
    )

    assert r.status_code == 200


@mock.patch("jira.JIRA.create_issue")
def test_jira_issue_default(
    mock_post, client: TestClient, api_key_headers: Dict[str, str]
) -> None:
    params = {"project_key": "JRA", "issue_type": "Bug", "issue_summary": "Test"}
    _body = {"body": "SAMPLE MESSAGE"}
    api_key_headers.update({"url": "https://jira.atlassian.com"})

    r = client.post(
        f"{settings.API_V1_STR}/jira/new_issue",
        json=_body,
        params=params,
        allow_redirects=True,
        headers=api_key_headers,
    )

    assert r.status_code == 200
