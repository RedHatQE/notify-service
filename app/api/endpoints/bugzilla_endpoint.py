from fastapi import Query, APIRouter, HTTPException, Body
import bugzilla
from app.core.config import settings
import xmlrpc.client
from app import schemas
from typing import Union


router = APIRouter()

@router.post("/new_bug", response_model=schemas.Msg)
async def new_bugzilla_bug(
    product: str = Query(
        ...,
        description="The product - i.e. Fedora"
    ),
    version: str = Query(
        ...,
        description="The product's version - i.e. rawhide"
    ),
    component: str = Query(
        ...,
        description="The product's component - i.e. python-bugzilla"
    ),
    summary: str = Query(
        ...,
        description="The summary of the bug"
    ),
    environment: Union[schemas.DictBody, schemas.TxtBody, schemas.BaseResultBody] = Body(
        ...,
        example={
            "body": "SAMPLE MESSAGE."
        },
        description="The body values for parse with the template, "
        "check samples at https://github.com/waynesun09/notify-service/tree/main/docs/sample"
    )):

    data = environment.body
    try:
        bzapi = bugzilla.Bugzilla(settings.BUGZILLA_URL, api_key=settings.BUGZILLA_API_KEY)
        bzapi.logged_in
    except xmlrpc.client.Fault:
        raise HTTPException(status_code=500, detail="Failed to connect - please check your URL / API key")

    createinfo = bzapi.build_createbug(
        product=product,
        version=version,
        component=component,
        summary=summary,
        description=data)
    try:
        newbug = bzapi.createbug(createinfo)
        return {"msg": "Created new bug id=%s url=%s" % (newbug.id, newbug.weburl)}
    except xmlrpc.client.Fault:
        return {"msg": "Failed - please check that your input to the fields is correct and valid"}