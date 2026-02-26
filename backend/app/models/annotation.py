# Annotation Model
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class Rectangle(BaseModel):
    x: float
    y: float
    width: float
    height: float


class Annotation(BaseModel):
    id: str = Field(default_factory=lambda: "anno_" + str(hash(None)))
    document_id: str
    page_index: int
    position: Rectangle
    content: str
    author: str
    color: str = "#FF5722"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
