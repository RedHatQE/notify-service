import enum
from typing import Union, Optional
from fastapi import FastAPI, Query, APIRouter, HTTPException, Body
from pydantic.networks import AnyHttpUrl

from app import schemas
from app.utils import utils
from app.core.config import settings

from jira import JIRA

router = APIRouter()

@router.post("/", response_model=schemas.Msg)
async def create_a_jira_issue(
    project_key:str = Query(
        None, description="Project key - i.e. CCITNOTES"
    ),
    issue_type:str = Query(
        None, description="Issue type - i.e. Bug/Task/Story/Epic/etc."
    ),
    issue_summary:str = Query(
        None, description="Required or a new ticket: Issue summary"
    ),
    template_name: str = Query(
        "jira_default",
        description="The jinja html template name without subfix, e.g. default. "
        "Check jinja mjml at: https://github.com/waynesun09/notify-service/blob/main/app/templates/src/"
    ),
    environment: Union[schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody] = Body(
        ...,
        example={
            "body": "SAMPLE MESSAGE."
        },
        description="The body values for parse with the template, "
        "check samples at https://github.com/waynesun09/notify-service/tree/main/docs/sample"
    ),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the template_name if given")):

    if project_key == None or issue_summary == None or issue_type == None:
        raise HTTPException(status_code=404, detail="Please input values for project_key, issue_summary, issue_description, and issue_type")

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

    token = settings.JIRA_TOKEN
    options = { 'server': settings.JIRA_URL }
    conn = JIRA(options, token_auth=token)

    issue_dict = {
        'project': project_key,
        'summary': issue_summary,
        'description': data,
        'issuetype': {'name': issue_type},
    }
    new_issue = conn.create_issue(fields=issue_dict)

    return {"msg": "Success - Posted a new ticket!"}
