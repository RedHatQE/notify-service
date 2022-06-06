import enum
from typing import Optional
from fastapi import FastAPI, Query, APIRouter, HTTPException

from app import schemas
from app.core.config import settings

from jira import JIRA

router = APIRouter()

@router.post("/", response_model=schemas.Msg)
async def create_a_jira_issue(
    project_key: Optional[str] = Query(
        None, description="Required for New Ticket: Project key - i.e. CCITNOTES"
    ),
    issue_summary: Optional[str] = Query(
        None, description="Required for New Ticket: Issue summary"
    ), 
    issue_description: Optional[str] = Query(
        None, description="Required for New Ticket: The issue description"
    ), 
    issue_type: Optional[str] = Query(
        None, description="Required for New Ticket: Bug/Task/Story/Epic/etc."
    )):
    
    token = settings.JIRA_TOKEN

    options = { 'server': settings.JIRA_URL }
    conn = JIRA(options, token_auth=token)
    
    if project_key == None or issue_summary == None or issue_description == None or issue_type == None:
        raise HTTPException(status_code=404, detail="Please input values for project_key, issue_summary, issue_description, and issue_type")
    issue_dict = {
        'project': project_key,
        'summary': issue_summary,
        'description': issue_description,
        'issuetype': {'name': issue_type},
    }
    #new_issue = conn.create_issue(fields=issue_dict)

    return {"msg": "Success - Posted a new ticket!"}
