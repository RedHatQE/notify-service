from unittest import mock
from typing import Dict
from httpx import Response

from fastapi.testclient import TestClient

from app.core.config import settings

@mock.patch('app.utils.message_bus.quick_send')
@mock.patch('app.utils.irc.send_message')
@mock.patch('httpx.AsyncClient.post', return_value=Response(status_code=200))
@mock.patch('emails.message.Message.send')
@mock.patch('jira.JIRA.create_issue')
@mock.patch('bugzilla.Bugzilla.update_bugs')
def test_multi_message_default(
        mock_send_email,
        mock_send_chat,
        mock_send_irc,
        mock_send_message_bus,
        mock_create_jira_issue,
        mock_add_bugzilla_comment,
        client: TestClient,
        api_key_headers: Dict[str, str]
) -> None:
    _target = ["email", "gchat", "slack", "irc", "message_bus", "jira", "bugzilla"]
    _irc_channel = "test"
    _email_to = "abc@example.com"
    _subject = "TEST"
    _message_bus_topic = "test"
    _jira_project_issue_key = "JRA"
    _jira_issue_type = "Bug"
    _jira_issue_summary = "Test"
    _bugzilla_bug_id = 12345
    params = {
        "target": _target,
        "irc_channel": _irc_channel,
        "email_to": _email_to,
        "subject": _subject,
        "message_bus_topic": _message_bus_topic,
        "jira_project_issue_key": _jira_project_issue_key,
        "jira_issue_type": _jira_issue_type,
        "jira_issue_summary": _jira_issue_summary,
        "bugzilla_bug_id": _bugzilla_bug_id
    }
    _body = {
        "body": "SAMPLE MESSAGE"
    }
    r = client.post(f"{settings.API_V1_STR}/message_multi_targets",
                    json=_body,
                    params=params,
                    allow_redirects=True,
                    headers=api_key_headers)
    assert r.status_code == 200
    assert r.text == '{"msg":"Message have been send to all targets [\'email\', \'gchat\', \'slack\', \'irc\', \'message_bus\', \'jira\', \'bugzilla\']"}'
