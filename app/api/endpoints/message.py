from typing import Any, List, Optional, Union
from pydantic.networks import AnyHttpUrl, EmailStr

from fastapi import APIRouter, Query, Body, status, HTTPException

from app import schemas
from app.core.config import settings
from app.api.endpoints import email, chat, irc, message_bus, jira, bugzilla_endpoint

router = APIRouter()

TARGET = ['email', 'gchat', 'slack', 'irc', 'message_bus', 'jira', 'bugzilla']

def param_err(err: str) -> Any:
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=err)


@router.post("/", response_model=schemas.Msg)
async def msg_multi_tgts(
    target: List[str] = Query(
        ...,
        enum=["email", "gchat", "slack", "irc", "message_bus", "jira", "bugzilla"],
        description="Targets: email, gchat, slack, irc, message_bus, jira, bugzilla"
    ),
    irc_channel: str = Query(
        None,
        description="IRC channel name start with '#' or a user name, e.g. channel #test or user john"
    ),
    email_to: List[EmailStr] = Query(
        None, description="Email address, e.g. abc@example.com"
    ),
    email_template_name: str = Query(
        "default",
        description="The jinja template name without subfix, e.g. default. "
        "Check jinja mjml at: https://github.com/waynesun09/notify-service/blob/main/app/templates/src/"
    ),
    email_template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the email_template_name if given"
    ),
    gchat_template_name: str = Query(
        "chat_default",
        description="The jinja template name without subfix, e.g. default. "
        "Check gchat jinja at: https://github.com/waynesun09/notify-service/blob/main/app/templates/build/"
    ),
    gchat_template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the gchat_template_name if given"
    ),
    slack_template_name: str = Query(
        "chat_default",
        description="The jinja template name without subfix, e.g. default. "
        "Check slack jinja at: https://github.com/waynesun09/notify-service/blob/main/app/templates/build/"
    ),
    slack_template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the slack_template_name if given"
    ),
    subject: str = Query(
        f"Notification from {settings.PROJECT_NAME}",
        description="The message subject"
    ),
    message_bus_topic: str = Query(
        settings.MSG_DEFAULT_TOPIC,
        description="The message topic or queue value, e.g. /topic/VirtualTopic.qe.ci.test.abc.test.complete"
    ),
    environment: Union[schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody] = Body(
        ...,
        example={
            "body": "SAMPLE PLAIN TEXT MESSAGE OR JSON DICT."
        },
        description="The body values for parse with template or send "
        "Check samples at https://github.com/waynesun09/notify-service/tree/main/docs/sample"
    ),
    gchat_webhook_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The gchat webhook url"
    ),
    slack_webhook_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The slack webhook url"
    ),
    jira_project_issue_key: str = Query(
        None, description="The issue key for adding a comment - i.e. CCITNOTES-50, project key for new issue - i.e. CCITNOTES"
    ),
    jira_issue_type: str = Query(
        "Task", enum=settings.JIRA_ISSUE_TYPE_LIST, description="Required for a new issue: - Issue type - i.e. Bug/Task/Story/Epic/etc."
    ),
    jira_issue_summary: str = Query(
        None, description="Required for a new issue: Issue summary"
    ),
    jira_template_name: str = Query(
        "jira_default",
        description="The jinja html template name without subfix, e.g. jira_default. "
        "Check jinja mjml at: https://github.com/waynesun09/notify-service/blob/main/app/templates/src/build"
    ),
    jira_template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the jira_template_name if given"
    ),
    bugzilla_bug_id: int = Query(
        None,
        description="The bug_id - i.e. 1997649"
    ),
    bugzilla_template_name: str = Query(
        "bugzilla_default",
        description="The jinja html template name without subfix, e.g. bugzilla_default. "
        "Check jinja mjml at: https://github.com/waynesun09/notify-service/blob/main/app/templates/src/build"
    ),
    bugzilla_template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the template_name if given")) -> Any:
    """
    Send text messages to multiple supported backends

    - **target**: target backend list of strings, i.e. ["email", "gchat", "slack"] required
    - **subject**: message subject, optional
    - **channel**: The irc channel name start with '#' or a user name, optional
    - **email_to**: email address, optional
    - **email_template_name**: email template name, optional
    - **email_template_url**: email template url, optional
    - **gchat_template_name**: gchat template name, optional
    - **gchat_template_url**: gchat template url, optional
    - **slack_template_name**: slack template name, optional
    - **slack_template_url**: slack template url, optional
    - **gchat_webhook_url**: gchat webhook url address, optional
    - **slack_webhook_url**: slack webhook url address, optional
    - **jira_project_issue_key**: Jira project/issue key, optional
    - **jira_issue_type**: Jira issue type, optional
    - **jira_issue_summary**: Jira issue summary, optional
    - **jira_template_name**: Jira template name, optional
    - **jira_template_url**: Jira template url, optional
    - **bugzilla_bug_id**: Bugzilla bug id, optional
    - **bugzilla_template_name**: Bugzilla template name, optional
    - **bugzilla_template_url**: Bugzilla template url, optional
    - **Request Body**: Check samples at https://github.com/waynesun09/notify-service/tree/main/docs/sample
    """

    for t in target:
        if t not in TARGET:
            detail = f"The target {t} is not supported"
            param_err(detail)

    if (("gchat" in target and not (gchat_webhook_url or settings.GCHAT_WEBHOOK_URL)) or
            ("slack" in target and not (slack_webhook_url or settings.SLACK_WEBHOOK_URL))):
        detail = "The chat webhook url has not been provided"
        param_err(detail)

    if 'irc' in target and not irc_channel:
        detail = "The IRC channel has not been provided"
        param_err(detail)

    if "email" in target and not email_to:
        detail = "The email address has not been provided"
        param_err(detail)

    if 'message_bus' in target and not message_bus_topic:
        detail = "The message bus topic has not been provided"
        param_err(detail)

    if 'jira' in target and not jira_project_issue_key:
        detail = "The Jira project/issue key has not been provided"
        param_err(detail)

    # Checking if the last char in the key is a digit - if it is not
    # it means that the user wanted to add a new issue
    if 'jira' in target and (not jira_project_issue_key[-1].isdigit()) and (not jira_issue_type or not jira_issue_summary):
        detail = "When creating a new Jira issue - jira_issue_type and jira_issue_summary are required"
        param_err(detail)

    if 'bugzilla' in target and not bugzilla_bug_id:
        detail = "The Bugzilla bug id has not been provided"
        param_err(detail)

    body = environment.body
    env = environment.copy()

    if 'gchat' in target:
        if not gchat_webhook_url:
            gchat_webhook_url = settings.GCHAT_WEBHOOK_URL
        await chat.send_message(
            'gchat',
            subject=subject,
            environment=environment,
            template_name=gchat_template_name,
            webhook_url=gchat_webhook_url,
            template_url=gchat_template_url
        )

    if 'slack' in target:
        if not slack_webhook_url:
            slack_webhook_url = settings.SLACK_WEBHOOK_URL
        await chat.send_message(
            'slack',
            subject=subject,
            environment=environment,
            template_name=slack_template_name,
            webhook_url=slack_webhook_url,
            template_url=slack_template_url
        )

    if 'irc' in target:
        # Only text is supported, so convert body to str
        text = "{}:\n{}".format(subject, str(environment.body))
        await irc.send_message(
            channel=irc_channel,
            message=text
        )

    if 'email' in target:
        await email.send_email(
            email_to,
            subject=subject,
            template_name=email_template_name,
            environment=environment,
            template_url=email_template_url
        )

    # Use environment copy as message bus backend could parse both random dict and text
    if 'message_bus' in target:
        message_bus.send_message(
            topic=message_bus_topic,
            environment=env
        )

    if 'jira' in target:
        # Means that it's a new comment
        if jira_project_issue_key[-1].isdigit():
            await jira.add_a_jira_comment(
                issue_key=jira_project_issue_key,
                template_name=jira_template_name,
                environment=environment,
                template_url=jira_template_url
            )
        else:
            await jira.create_a_jira_issue(
                project_key=jira_project_issue_key,
                issue_type=jira_issue_type,
                issue_summary=jira_issue_summary,
                template_name=jira_template_name,
                environment=environment,
                template_url=jira_template_url
            )

    if 'bugzilla' in target:
        await bugzilla_endpoint.add_comment(
            bug_id=bugzilla_bug_id,
            environment=environment,
            template_name=bugzilla_template_name,
            template_url=bugzilla_template_url
        )

    return {"msg": f"Message have been send to all targets {target}"}
