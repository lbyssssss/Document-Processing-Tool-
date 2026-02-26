# Search API
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import uuid
import shutil

from app.core.config import settings
from app.services.search_service import (
    SearchService,
    SearchOptions as ServiceSearchOptions,
    SearchResult as ServiceSearchResult,
)

router = APIRouter()

# 初始化搜索服务
search_service = SearchService(settings.index_dir)

# 确保索引目录存在
Path(settings.index_dir).mkdir(parents=True, exist_ok=True)


class SearchOptionsPydantic(BaseModel):
    case_sensitive: bool = False
    whole_word: bool = False
    regex: bool = False
    page_limit: int = 20


class SearchResultPydantic(BaseModel):
    page_index: int
    text: str
    position: dict
    highlights: List[str] = []


class IndexBuildResultPydantic(BaseModel):
    success: bool
    document_id: str
    total_pages: int = 0
    indexed_pages: int = 0
    error: Optional[str] = None


def _to_pydantic_result(result: ServiceSearchResult) -> SearchResultPydantic:
    """转换服务结果为API结果"""
    return SearchResultPydantic(
        page_index=result.page_index,
        text=result.text,
        position=result.position,
        highlights=result.highlights,
    )


async def _save_upload_file(file: UploadFile) -> Path:
    """保存上传的文件"""
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    filename = f"{file_id}{file_ext}"
    file_path = Path(settings.upload_dir) / filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


@router.get("/search/{document_id}", response_model=List[SearchResultPydantic])
async def search_document(
    document_id: str,
    query: str,
    options: Optional[SearchOptionsPydantic] = None,
):
    """在文档中搜索"""
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="查询不能为空")

    service_options = ServiceSearchOptions(
        case_sensitive=options.case_sensitive if options else False,
        whole_word=options.whole_word if options else False,
        regex=options.regex if options else False,
        page_limit=options.page_limit if options else 20,
    )

    results = search_service.search(document_id, query, service_options)

    return [_to_pydantic_result(r) for r in results]


@router.post("/search/index/{document_id}", response_model=IndexBuildResultPydantic)
async def build_index(
    document_id: str,
    file: UploadFile = File(...),
):
    """为文档建立搜索索引"""
    try:
        # 保存上传的文件
        file_path = await _save_upload_file(file)

        # 建立索引
        result = search_service.build_index(document_id, str(file_path))

        return IndexBuildResultPydantic(
            success=result.get("success", False),
            document_id=document_id,
            total_pages=result.get("total_pages", 0),
            indexed_pages=result.get("indexed_pages", 0),
            error=result.get("error"),
        )

    except Exception as e:
        return IndexBuildResultPydantic(
            success=False,
            document_id=document_id,
            error=str(e),
        )


@router.get("/search/index/{document_id}/info")
async def get_index_info(document_id: str):
    """获取文档索引信息"""
    info = search_service.get_index_info(document_id)
    return info


@router.delete("/search/index/{document_id}")
async def delete_index(document_id: str):
    """删除文档的索引"""
    success = search_service.delete_index(document_id)
    return {"success": success}
