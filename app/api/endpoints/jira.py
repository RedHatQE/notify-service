import enum
from typing import Optional
from fastapi import FastAPI, Query, APIRouter, HTTPException

from app import schemas
from app.core.config import settings

from jira import JIRA

router = APIRouter()

@router.post("/", response_model=schemas.Msg)
async def create_a_jira_issue(
    action: str = Query(
        "New Ticket", enum=["New Ticket", "Add Comment"], description="Please choose New Ticket to create a new ticket or Add Comment to add comment to an existing ticket"
    ),
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
    ),
    comment_key: Optional[str] = Query(
        None, description="Required for Add Comment: The comment key - i.e. CCITNOTES-50"
    ),
    comment_description: Optional[str] = Query(
        None, description="Required for Add Comment: The comment description"
    )):
    
    token = settings.JIRA_TOKEN

    options = { 'server': settings.JIRA_URL }
    conn = JIRA(options, token_auth=token)
    
    if action == "New Ticket":
        if project_key == None or issue_summary == None or issue_description == None or issue_type == None:
            raise HTTPException(status_code=404, detail="Please input values for project_key, issue_summary, issue_description, and issue_type")
        issue_dict = {
            'project': project_key,
            'summary': issue_summary,
            'description': issue_description,
            'issuetype': {'name': issue_type},
        }
        new_issue = conn.create_issue(fields=issue_dict)

        return {"msg": "Success - Posted a new ticket!"}
    
    elif action == "Add Comment":
        if comment_key == None or comment_description == None:
            raise HTTPException(status_code=404, detail="Please input values for comment_key and comment_description")
        
        comment = conn.add_comment(comment_key, comment_description)

        return {"msg": "Success - Added a new comment"}

    else:
        raise HTTPException(status_code=404, detail="Only supports New Ticket and Add Comment")