from fastapi import APIRouter

from app.api.endpoints import bugzilla_endpoint
from app.api.endpoints import chat
from app.api.endpoints import email
from app.api.endpoints import irc
from app.api.endpoints import jira
from app.api.endpoints import message
from app.api.endpoints import message_bus
from app.api.endpoints import sms
from app.api.endpoints import template
from app.api.endpoints import utils

api_router = APIRouter()
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(template.router, prefix="/template", tags=["template"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(irc.router, prefix="/irc", tags=["irc"])
api_router.include_router(
    message_bus.router, prefix="/message_bus", tags=["message_bus"]
)
api_router.include_router(
    message.router, prefix="/message_multi_targets", tags=["message_multi_targets"]
)
api_router.include_router(sms.router, prefix="/sms", tags=["sms"])
api_router.include_router(jira.router, prefix="/jira", tags=["jira"])
api_router.include_router(
    bugzilla_endpoint.router, prefix="/bugzilla", tags=["bugzilla"]
)
