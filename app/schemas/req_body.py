from typing import Optional
from pydantic import BaseModel

from . import result


class TxtBody(BaseModel):
    body: str
    project_name: Optional[str] = None

class DictBody(BaseModel):
    body: dict
    project_name: Optional[str] = None
    headers: Optional[dict] = None

class BaseResultBody(DictBody):
    body: result.Content
