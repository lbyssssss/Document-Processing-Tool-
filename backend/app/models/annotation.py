# Annotation Model
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class Rectangle(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Annotation(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str
    page_index: int
    position: Rectangle
    content: str
    author: str = "anonymous"
    color: str = "#FF5722"
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(default_factory=datetime.now)
