# Search API
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class SearchOptions(BaseModel):
    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False


class SearchResult(BaseModel):
    page_index: int
    text: str
    position: dict


@router.get("/search/{document_id}", response_model=List[SearchResult])
async def search_document(
    document_id: str,
    query: str,
    options: Optional[SearchOptions] = None,
):
    """在文档中搜索"""
    # TODO: Implement search logic
    return []


@router.post("/search/index/{document_id}")
async def build_index(document_id: str):
    """为文档建立搜索索引"""
    # TODO: Implement index building
    return {"status": "not implemented"}
