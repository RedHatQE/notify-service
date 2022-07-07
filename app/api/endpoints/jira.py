from typing import Optional, Union
from fastapi import Query, APIRouter, HTTPException, Body
from pydantic.networks import AnyHttpUrl

from app import schemas
from app.utils import utils
from app.core.config import settings

import jira
from jira import JIRA

router = APIRouter()

@router.post("/add_comment", response_model=schemas.Msg)
async def add_a_jira_comment(
    issue_key: str = Query(
        None, description="Required for Add Comment: The issue key - i.e. CCITNOTES-50"
    ),
    template_name: str = Query(
        "jira_default",
        description="The jinja html template name without subfix, e.g. jira_default. "
        "Check jinja template at: https://github.com/RedHatQE/notify-service/tree/main/app/templates/build"
    ),
    environment: Union[schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody] = Body(
        ...,
        example={
            "body": "SAMPLE MESSAGE."
        },
        description="The body values for parse with the template, "
        "check samples at https://github.com/RedHatQE/notify-service/tree/main/docs/sample"
    ),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the template_name if given"
    ),
    jira_token: Optional[str] = Query(
        None,
        description="A Jira personal token, it will overring the existing api key in the environment configuration")):

    if issue_key is None:
        raise HTTPException(status_code=404, detail="Please input values for issue_key")

    env = {}
    if (not template_url and
            (isinstance(environment.body, str) or
                (template_name == 'jira_default' and "body" not in environment.body))):
        # Set 'body' in env dict, this will work with default template
        env["body"] = environment.body
    else:
        # Pass the body dict value to the env dict, it will be parsed by specific template
        env = environment.body
    data = await utils.get_template(template_name, None, '.jinja', env)

    if jira_token is None:
        token = settings.JIRA_TOKEN
    else:
        token = jira_token

    options = {'server': settings.JIRA_URL}
    try:
        conn = JIRA(options, token_auth=token)
        comment = conn.add_comment(issue_key, data)
        return {"msg": "Successfully added a comment"}
    except jira.exceptions.JIRAError:
        raise HTTPException(status_code=500, detail="Failed to connect - please check your token/issue_key")


@router.post("/new_issue", response_model=schemas.Msg)
async def create_a_jira_issue(
    project_key: str = Query(
        None, description="Project key - i.e. CCITNOTES"
    ),
    issue_type: str = Query(
        "Task", enum=settings.JIRA_ISSUE_TYPE_LIST, description="Issue type - i.e. Bug/Task/Story/Epic/etc."
    ),
    issue_summary: str = Query(
        None, description="Required for a new ticket: Issue summary"
    ),
    template_name: str = Query(
        "jira_default",
        description="The jinja html template name without subfix, e.g. default. "
        "Check jinja template at: https://github.com/RedHatQE/notify-service/tree/main/app/templates/build"
    ),
    environment: Union[schemas.TxtBody, schemas.JiraBody, schemas.BaseResultBody] = Body(
        ...,
        example={
            "body": "SAMPLE MESSAGE."
        },
        description="The body values for parse with the template, "
        "check samples at https://github.com/RedHatQE/notify-service/tree/main/docs/sample"
    ),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the template_name if given"
    ),
    jira_token: Optional[str] = Query(
        None,
        description="A Jira personal token, it will overring the existing api key in the environment configuration")):

    if project_key is None or issue_summary is None or issue_type is None:
        raise HTTPException(status_code=400, detail="Please input values for project_key, issue_summary, issue_description, and issue_type")

    env = {}
    if (not template_url and
            (isinstance(environment.body, str) or
                (template_name == 'jira_default' and "body" not in environment.body))):
        # Set 'body' in env dict, this will work with default template
        env["body"] = environment.body
    else:
        # Pass the body dict value to the env dict, it will be parsed by specific template
        env = environment.body

    data = await utils.get_template(template_name, None, '.jinja', env)

    if jira_token is None:
        token = settings.JIRA_TOKEN
    else:
        token = jira_token
    options = {'server': settings.JIRA_URL}

    try:
        conn = JIRA(options, token_auth=token)
        # Extract components and reformat to match Jira API
        components = []
        if environment.components != []:
            for component in environment.components:
                components.append({'name': component})

        issue_dict = {
            'project': project_key,
            'summary': issue_summary,
            'description': data,
            'issuetype': {'name': issue_type},
            'components': components,
            'labels': environment.labels,
            'versions': environment.affects_versions,
            'fixVersions': environment.fix_versions
        }
        new_issue = conn.create_issue(fields=issue_dict)
        return {"msg": "Success - Posted a new ticket!"}

    except jira.exceptions.JIRAError:
        raise HTTPException(status_code=500, detail="Failed to connect - please check your token/project_key")
