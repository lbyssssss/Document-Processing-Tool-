# Page Model
from pydantic import BaseModel
from typing import Optional, List


class PageContent(BaseModel):
    text: Optional[str] = None
    elements: Optional[List[dict]] = None


class Page(BaseModel):
    index: int
    width: float
    height: float
    rotation: int = 0
    thumbnail: str
    content: Optional[PageContent] = None
