# Merge API
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class SelectedPage(BaseModel):
    id: str
    document_id: str
    page_index: int
    original_document_name: str
    thumbnail: str
    page_width: float
    page_height: float
    rotation: int


class MergeConfig(BaseModel):
    page_size: str = "auto"
    orientation: str = "keep-original"
    output_file_name: str
    include_bookmarks: bool = False
    metadata: Optional[dict] = None


class MergeResult(BaseModel):
    success: bool
    output_path: Optional[str] = None
    total_pages: int
    warnings: List[str] = []
    error: Optional[str] = None


@router.post("/merge/select-page")
async def select_page(page: SelectedPage):
    """选择页面添加到拼接队列"""
    # TODO: Implement page selection
    return {"status": "not implemented"}


@router.delete("/merge/select-page/{page_id}")
async def deselect_page(page_id: str):
    """取消选择页面"""
    # TODO: Implement page deselection
    return {"status": "not implemented"}


@router.post("/merge/select-range")
async def select_page_range(document_id: str, start: int, end: int):
    """按范围选择页面"""
    # TODO: Implement range selection
    return {"status": "not implemented"}


@router.post("/merge/toggle-all/{document_id}")
async def toggle_all_pages(document_id: str):
    """全选/取消全选文档的所有页面"""
    # TODO: Implement toggle all
    return {"status": "not implemented"}


@router.post("/merge/reorder")
async def reorder_page(page_id: str, new_index: int):
    """调整拼接队列中页面顺序"""
    # TODO: Implement reorder
    return {"status": "not implemented"}


@router.delete("/merge/queue")
async def clear_queue():
    """清空拼接队列"""
    # TODO: Implement clear queue
    return {"status": "not implemented"}


@router.get("/merge/queue", response_model=List[SelectedPage])
async def get_queue():
    """获取当前拼接队列"""
    # TODO: Implement get queue
    return []


@router.post("/merge/execute", response_model=MergeResult)
async def merge_documents(config: MergeConfig):
    """生成合并后的PDF"""
    # TODO: Implement merge logic
    return MergeResult(
        success=False,
        total_pages=0,
        error="Not implemented yet",
    )
