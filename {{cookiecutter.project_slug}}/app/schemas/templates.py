from typing import Optional

from pydantic import BaseModel


class TmpltBase(BaseModel):
    filename: Optional[str] = None


class Tmplt(TmpltBase):
    content: str
