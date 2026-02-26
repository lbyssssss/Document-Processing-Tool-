# Page Management API
from fastapi import APIRouter

router = APIRouter()


@router.get("/page/{document_id}/{page_number}")
async def get_page(document_id: str, page_number: int):
    """获取指定页面"""
    return {"page_number": page_number, "content": ""}


@router.put("/page/{document_id}/{page_number}")
async def update_page(document_id: str, page_number: int):
    """更新页面"""
    return {"success": True}


@router.delete("/page/{document_id}/{page_number}")
async def delete_page(document_id: str, page_number: int):
    """删除页面"""
    return {"success": True}
