from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import EmailStr

from . import result


class EmailBase(BaseModel):
    email: Optional[EmailStr] = None


class EmailSend(EmailBase):
    msg: str


class EmailResult(BaseModel):
    pre_header: Optional[str] = None
    begin: Optional[str] = None
    content: List[result.Result]
    end: Optional[str] = None
