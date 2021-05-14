from typing import Optional, List
from pydantic import BaseModel
from pydantic.networks import AnyHttpUrl


class Case(BaseModel):
    name: str
    href: Optional[AnyHttpUrl] = None
    status: str

class Result(BaseModel):
    title: Optional[str] = None
    cases: List[Case]
    name: Optional[str] = None
    link: Optional[AnyHttpUrl] = None
    more: Optional[str] = None

class Content(BaseModel):
    content: List[Result]
