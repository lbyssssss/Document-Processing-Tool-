# Page Management API
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import shutil
import uuid

from app.core.config import settings
from app.services.page_service import PageService

router = APIRouter()

# 初始化页面管理服务
page_service = PageService(settings.upload_dir)


class PageInfoPydantic(BaseModel):
    """页面信息"""
    index: int
    width: float
    height: float
    rotation: int


class DocumentPagesPydantic(BaseModel):
    """文档页面列表"""
    success: bool
    total_pages: int
    pages: List[PageInfoPydantic]


class InsertPageRequestPydantic(BaseModel):
    """插入页面请求"""
    index: int
    page_data: Optional[dict] = None


class RotatePageRequestPydantic(BaseModel):
    """旋转页面请求"""
    degrees: int


class MovePageRequestPydantic(BaseModel):
    """移动页面请求"""
    from_index: int
    to_index: int


class MergePagesRequestPydantic(BaseModel):
    """合并页面请求"""
    indices: List[int]


@router.get("/page/document/{document_id}/info", response_model=DocumentPagesPydantic)
async def get_document_pages_info(document_id: str):
    """获取文档的所有页面信息

    Args:
        document_id: 文档ID

    Returns:
        页面信息列表
    """
    # 查找文档文件
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    result = page_service.get_document_pages(str(doc_path))

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "获取页面信息失败"))

    return DocumentPagesPydantic(
        success=result["success"],
        total_pages=result["total_pages"],
        pages=result["pages"],
    )


@router.get("/page/{document_id}/{page_number}")
async def get_page_thumbnail(document_id: str, page_number: int):
    """获取页面缩略图

    Args:
        document_id: 文档ID
        page_number: 页码（从1开始）

    Returns:
        缩略图base64数据
    """
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    thumbnail = await page_service.get_thumbnail(document_id, str(doc_path), page_number - 1)

    if thumbnail is None:
        raise HTTPException(status_code=500, detail="生成缩略图失败")

    return {"thumbnail": thumbnail}


@router.post("/page/{document_id}/insert")
async def insert_page(document_id: str, request: InsertPageRequestPydantic):
    """在指定位置插入空白页面

    Args:
        document_id: 文档ID
        request: 插入请求

    Returns:
        操作结果
    """
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    result = page_service.insert(
        document_id=document_id,
        pdf_path=str(doc_path),
        index=request.index,
        page_data=request.page_data,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "插入页面失败"))

    return result


@router.delete("/page/{document_id}/{page_number}")
async def delete_page(document_id: str, page_number: int):
    """删除指定页面

    Args:
        document_id: 文档ID
        page_number: 页码（从1开始）

    Returns:
        操作结果
    """
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    result = page_service.delete(
        document_id=document_id,
        pdf_path=str(doc_path),
        index=page_number - 1,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "删除页面失败"))

    return result


@router.post("/page/{document_id}/move")
async def move_page(document_id: str, request: MovePageRequestPydantic):
    """移动页面到新位置

    Args:
        document_id: 文档ID
        request: 移动请求

    Returns:
        操作结果
    """
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    result = page_service.move(
        document_id=document_id,
        pdf_path=str(doc_path),
        from_index=request.from_index,
        to_index=request.to_index,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "移动页面失败"))

    return result


@router.post("/page/{document_id}/{page_number}/rotate")
async def rotate_page(document_id: str, page_number: int, request: RotatePageRequestPydantic):
    """旋转指定页面

    Args:
        document_id: 文档ID
        page_number: 页码（从1开始）
        request: 旋转请求

    Returns:
        操作结果
    """
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    result = page_service.rotate(
        document_id=document_id,
        pdf_path=str(doc_path),
        index=page_number - 1,
        degrees=request.degrees,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "旋转页面失败"))

    return result


@router.post("/page/{document_id}/merge")
async def merge_pages(document_id: str, request: MergePagesRequestPydantic):
    """合并多个页面

    Args:
        document_id: 文档ID
        request: 合并请求

    Returns:
        操作结果
    """
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    result = page_service.merge(
        document_id=document_id,
        pdf_path=str(doc_path),
        indices=[i - 1 for i in request.indices],  # 转换为0-based索引
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "合并页面失败"))

    return result


@router.post("/page/{document_id}/{page_number}/split")
async def split_page(document_id: str, page_number: int):
    """拆分指定页面

    Args:
        document_id: 文档ID
        page_number: 页码（从1开始）

    Returns:
        操作结果
    """
    doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"

    if not doc_path.exists():
        raise HTTPException(status_code=404, detail="文档不存在")

    result = page_service.split(
        document_id=document_id,
        pdf_path=str(doc_path),
        index=page_number - 1,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "拆分页面失败"))

    return result


@router.get("/page/{document_id}/temp")
async def get_temp_file(document_id: str):
    """获取文档的临时文件（用于预览）

    Args:
        document_id: 文档ID

    Returns:
        临时文件信息
    """
    temp_path = page_service.get_temp_file(document_id)

    if not temp_path:
        raise HTTPException(status_code=404, detail="没有找到临时文件")

    temp_file = Path(temp_path)
    if not temp_file.exists():
        raise HTTPException(status_code=404, detail="临时文件不存在")

    return {
        "path": temp_path,
        "filename": temp_file.name,
        "size": temp_file.stat().st_size,
    }
