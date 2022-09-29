import xmlrpc.client
from typing import Optional
from typing import Union

import bugzilla
from fastapi import APIRouter
from fastapi import Body
from fastapi import HTTPException
from fastapi import Query
from pydantic.networks import AnyHttpUrl

from app import schemas
from app.core.config import settings
from app.utils import utils


router = APIRouter()


@router.post("/new_bug", response_model=schemas.Msg)
async def new_bug(
    product: str = Query(..., description="The product - i.e. Fedora"),
    version: str = Query(..., description="The product's version - i.e. rawhide"),
    component: str = Query(
        ..., description="The product's component - i.e. python-bugzilla"
    ),
    summary: str = Query(..., description="The summary of the bug"),
    environment: Union[
        schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody
    ] = Body(
        ...,
        example={"body": "SAMPLE MESSAGE."},
        description="The body values for parse with the template, "
        "check samples at https://github.com/RedHatQE/notify-service/tree/main/docs/sample",
    ),
    template_name: str = Query(
        "bugzilla_default",
        description="The jinja template name without subfix, e.g. bugzilla_default. "
        "Check jinja templates at: https://github.com/RedHatQE/notify-service/tree/main/app/templates/build",
    ),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the template_name if given",
    ),
    api_key: Optional[str] = Query(
        None,
        description="A Bugzilla API key, it will overring the existing api key in the environment configuration",
    ),
):

    env = {}
    if not template_url and (
        isinstance(environment.body, str)
        or (template_name == "bugzilla_default" and "body" not in environment.body)
    ):
        # Set 'body' in env dict, this will work with default template
        env["body"] = environment.body
    else:
        # Pass the body dict value to the env dict, it will be parsed by specific template
        env = environment.body

    data = await utils.get_template(template_name, None, ".jinja", env)

    if api_key is None:
        current_api_key = settings.BUGZILLA_API_KEY
    else:
        current_api_key = api_key

    try:
        bz_api = bugzilla.Bugzilla(settings.BUGZILLA_URL, api_key=current_api_key)
        bug_info = bz_api.build_createbug(
            product=product,
            version=version,
            component=component,
            summary=summary,
            description=data,
        )
        bug = bz_api.createbug(bug_info)
        return {"msg": "Created new bug id=%s url=%s" % (bug.id, bug.weburl)}
    except xmlrpc.client.Fault:
        raise HTTPException(
            status_code=500,
            detail="Failed - please check your URL / API key and your input fields are correct",
        )


@router.post("/add_comment", response_model=schemas.Msg)
async def add_comment(
    bug_id: int = Query(..., description="The bug_id - i.e. 1997649"),
    environment: Union[
        schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody
    ] = Body(
        ...,
        example={"body": "SAMPLE MESSAGE."},
        description="The body values for parse with the template, "
        "check samples at https://github.com/RedHatQE/notify-service/tree/main/docs/sample",
    ),
    template_name: str = Query(
        "bugzilla_default",
        description="The jinja template name without subfix, e.g. bugzilla_default. "
        "Check jinja template at: https://github.com/RedHatQE/notify-service/tree/main/app/templates/build",
    ),
    template_url: Optional[AnyHttpUrl] = Query(
        None,
        description="The remote teamplate url, it will override the template_name if given",
    ),
    api_key: Optional[str] = Query(
        None,
        description="A Bugzilla API key, it will overring the existing api key in the environment configuration",
    ),
):

    env = {}
    if not template_url and (
        isinstance(environment.body, str)
        or (template_name == "bugzilla_default" and "body" not in environment.body)
    ):
        # Set 'body' in env dict, this will work with default template
        env["body"] = environment.body
    else:
        # Pass the body dict value to the env dict, it will be parsed by specific template
        env = environment.body

    data = await utils.get_template(template_name, None, ".jinja", env)

    if api_key is None:
        current_api_key = settings.BUGZILLA_API_KEY
    else:
        current_api_key = api_key

    try:
        bz_api = bugzilla.Bugzilla(settings.BUGZILLA_URL, api_key=current_api_key)
        update = bz_api.build_update(comment=data)
        bz_api.update_bugs([bug_id], update)
        return {"msg": f"Successfully added a comment to a bug with id: {bug_id}"}
    except xmlrpc.client.Fault:
        raise HTTPException(
            status_code=500,
            detail="Failed - please check your URL / API key and your bug id",
        )
