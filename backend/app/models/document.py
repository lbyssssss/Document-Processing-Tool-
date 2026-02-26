# Document Model
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from typing import Optional


class DocumentType(str, Enum):
    PDF = "pdf"
    WORD = "word"
    EXCEL = "excel"
    PPT = "ppt"
    IMAGE = "image"


class DocumentMetadata(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = None
    producer: Optional[str] = None
    creation_date: Optional[datetime] = None
    modification_date: Optional[datetime] = None


class Document(BaseModel):
    id: str = Field(default_factory=lambda: "doc_" + str(hash(None)))
    name: str
    type: DocumentType
    size: int
    file_path: str
    created_at: datetime = Field(default_factory=datetime.now)
    modified_at: datetime = Field(default_factory=datetime.now)
    page_count: int = 0
    thumbnail_path: Optional[str] = None
    metadata: Optional[DocumentMetadata] = None
