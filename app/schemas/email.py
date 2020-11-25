from typing import Optional

from pydantic import BaseModel, EmailStr


class EmailBase(BaseModel):
    email: Optional[EmailStr] = None


class EmailSend(EmailBase):
    msg: str
