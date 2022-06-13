from typing import List, Optional
from pydantic import BaseModel

from . import result


class TxtBody(BaseModel):
    body: str
    project_name: Optional[str] = None
    components: Optional[List[str]] = []
    labels: Optional[List[str]] = []
    affects_versions: Optional[List[str]] = []
    fix_versions: Optional[List[str]] = []

class DictBody(BaseModel):
    body: dict
    project_name: Optional[str] = None
    headers: Optional[dict] = None

class BaseResultBody(DictBody):
    body: result.Content

class JiraBody(BaseModel):
    body: dict
    components: Optional[List[str]] = []
    labels: Optional[List[str]] = []
    affects_versions: Optional[List[str]] = []
    fix_versions: Optional[List[str]] = []
