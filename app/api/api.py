from fastapi import APIRouter

from app.api.endpoints import email, chat, irc, message_bus, sms, template, utils, message

api_router = APIRouter()
api_router.include_router(email.router, prefix="/email", tags=["email"])
api_router.include_router(template.router, prefix="/template", tags=["template"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(irc.router, prefix="/irc", tags=["irc"])
api_router.include_router(message_bus.router, prefix="/message_bus", tags=["message_bus"])
api_router.include_router(message.router, prefix="/message_multi_targets", tags=["message_multi_targets"])
api_router.include_router(sms.router, prefix="/sms", tags=["sms"])
