from typing import Optional
from pydantic import BaseModel


class Msg(BaseModel):
    msg: str

class TxtBody(BaseModel):
    body: str
    project_name: Optional[str] = None

class DictBody(BaseModel):
    body: dict
    project_name: Optional[str] = None
    headers: Optional[dict] = None
