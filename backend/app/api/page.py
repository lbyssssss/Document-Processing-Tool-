# Page Management API
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import uuid
import shutil
import base64

from app.core.config import settings
from app.services.page_service import PageService

router = APIRouter()

# 初始化页面管理服务
page_service = PageService(
    upload_dir=settings.upload_dir,
    output_dir=settings.output_dir,
    thumbnail_dir=settings.thumbnail_dir,
)


class PageOperationResult(BaseModel):
    success: bool
    message: str
    page_count: int = 0
    error: Optional[str] = None


class PageInfo(BaseModel):
    page_number: int
    width: float
    height: float
    rotation: int = 0
    thumbnail: Optional[str] = None


@router.get("/page/{document_id}")
async def list_pages(document_id: str):
    """获取文档的所有页面信息"""
    try:
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 获取页面信息
        result = page_service.list_pages(doc_path)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/page/{document_id}/{page_number}")
async def get_page(document_id: str, page_number: int):
    """获取指定页面信息"""
    try:
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 获取页面信息
        result = page_service.get_page(doc_path, page_number)
        
        if not result.get("success"):
            if "索引越界" in result.get("error", ""):
                raise HTTPException(status_code=404, detail=result.get("error"))
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/page/{document_id}/{page_number}/thumbnail")
async def get_page_thumbnail(document_id: str, page_number: int, size: int = 300):
    """获取页面缩略图"""
    try:
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 获取缩略图
        result = page_service.get_thumbnail(doc_path, page_number, size)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "thumbnail": result["thumbnail"],
            "width": result["width"],
            "height": result["height"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/page/{document_id}/insert")
async def insert_page(document_id: str, page_number: int, file: Optional[UploadFile] = None):
    """在指定位置插入页面"""
    try:
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 插入页面
        result = page_service.insert_page(doc_path, page_number, file)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/page/{document_id}/{page_number}", response_model=PageOperationResult)
async def delete_page(document_id: str, page_number: int):
    """删除页面"""
    try:
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 删除页面
        result = page_service.delete_page(doc_path, page_number)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return PageOperationResult(
            success=True,
            message="页面删除成功",
            page_count=result["page_count"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/page/{document_id}/{page_number}/move")
async def move_page(document_id: str, page_number: int, new_page_number: int):
    """移动页面到新位置"""
    try:
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 移动页面
        result = page_service.move_page(doc_path, page_number, new_page_number)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/page/{document_id}/{page_number}/rotate")
async def rotate_page(document_id: str, page_number: int, degrees: int):
    """旋转页面"""
    try:
        # 验证旋转角度
        if degrees not in [90, 180, 270]:
            raise HTTPException(status_code=400, detail="旋转角度必须是90、180或270度")
        
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 旋转页面
        result = page_service.rotate_page(doc_path, page_number, degrees)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/page/{document_id}/merge")
async def merge_pages(document_id: str, page_numbers: List[int]):
    """合并多个页面为一个页面"""
    try:
        if len(page_numbers) < 2:
            raise HTTPException(status_code=400, detail="至少需要2个页面进行合并")
        
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 合并页面
        result = page_service.merge_pages(doc_path, page_numbers)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/page/{document_id}/{page_number}/split")
async def split_page(document_id: str, page_number: int, split_type: str = "vertical"):
    """拆分页面"""
    try:
        # 验证拆分类型
        if split_type not in ["vertical", "horizontal"]:
            raise HTTPException(status_code=400, detail="拆分类型必须是vertical或horizontal")
        
        # 查找文档
        doc_path = Path(settings.upload_dir) / f"{document_id}.pdf"
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="文档不存在")
        
        # 拆分页面
        result = page_service.split_page(doc_path, page_number, split_type)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/page/{document_id}/upload")
async def upload_document_for_page_management(document_id: str, file: UploadFile = File(...)):
    """上传文档用于页面管理"""
    try:
        # 保存文件
        file_ext = Path(file.filename).suffix
        target_filename = f"{document_id}.pdf"
        target_path = Path(settings.upload_dir) / target_filename
        
        # 确保是PDF
        if file_ext.lower() != '.pdf':
            raise HTTPException(status_code=400, detail="只支持PDF格式")
        
        with open(target_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        
        # 获取页面信息
        result = page_service.list_pages(target_path)
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "total_pages": result.get("total_pages", 0),
            "message": "文档上传成功",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
