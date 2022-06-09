from typing import Optional, Union
from fastapi import Query, APIRouter, HTTPException, Body
from pydantic.networks import AnyHttpUrl

from app import schemas
from app.utils import utils
from app.core.config import settings

from jira import JIRA

router = APIRouter()

@router.post("/", response_model=schemas.Msg)
async def add_a_jira_comment(
    comment_key: str = Query(
        None, description="Required for Add Comment: The comment key - i.e. CCITNOTES-50"
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

    options = {'server': settings.JIRA_URL}
    conn = JIRA(options, token_auth=token)

    if comment_key is None:
        raise HTTPException(status_code=404, detail="Please input values for comment_key")

    comment = conn.add_comment(comment_key, data)
    return {"msg": "Successfully added a comment"}
