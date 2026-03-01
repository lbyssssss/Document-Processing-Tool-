# Merge API
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import shutil

from app.core.config import settings
from app.services.merge_service import (
    MergeService,
    SelectedPage as MergeServiceSelectedPage,
    MergeConfig as MergeServiceMergeConfig,
    MergeResult as MergeServiceMergeResult,
)

router = APIRouter()

# 初始化合并服务
merge_service = MergeService()


class SelectedPagePydantic(BaseModel):
    id: str
    document_id: str
    page_index: int
    original_document_name: str
    thumbnail: str
    page_width: float
    page_height: float
    rotation: int


class MergeConfigPydantic(BaseModel):
    page_size: str = "auto"
    orientation: str = "keep-original"
    output_file_name: str
    include_bookmarks: bool = False
    metadata: Optional[dict] = None


class MergeResultPydantic(BaseModel):
    success: bool
    output_path: Optional[str] = None
    total_pages: int = 0
    warnings: List[str] = []
    error: Optional[str] = None


def _to_pydantic_page(page: MergeServiceSelectedPage) -> SelectedPagePydantic:
    """转换服务页面为API页面模型"""
    return SelectedPagePydantic(
        id=page.id,
        document_id=page.document_id,
        page_index=page.page_index,
        original_document_name=page.original_document_name,
        thumbnail=page.thumbnail,
        page_width=page.page_width,
        page_height=page.page_height,
        rotation=page.rotation,
    )


def _to_service_config(config: MergeConfigPydantic) -> MergeServiceMergeConfig:
    """转换API配置为服务配置"""
    return MergeServiceMergeConfig(
        page_size=config.page_size,
        orientation=config.orientation,
        output_file_name=config.output_file_name,
        include_bookmarks=config.include_bookmarks,
        metadata=config.metadata,
    )


def _to_pydantic_result(result: MergeServiceMergeResult) -> MergeResultPydantic:
    """转换服务结果为API结果"""
    return MergeResultPydantic(
        success=result.success,
        output_path=result.output_path,
        total_pages=result.total_pages,
        warnings=result.warnings,
        error=result.error,
    )


@router.post("/merge/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """上传文档用于合并"""
    import uuid
    import logging

    logger = logging.getLogger(__name__)

    logger.info(f"Received file: {file.filename}, content_type: {file.content_type}")

    # 验证文件类型
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")

    # 更宽容的文件名检查
    filename_lower = file.filename.lower()
    if not filename_lower.endswith('.pdf'):
        logger.warning(f"File extension check failed for: {file.filename}")
        raise HTTPException(status_code=400, detail="只支持PDF格式文件")

    # 生成文档ID
    doc_id = str(uuid.uuid4())

    # 目标路径
    target_filename = f"{doc_id}.pdf"
    target_path = Path(settings.upload_dir) / target_filename

    # 确保上传目录存在
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 保存上传的文件
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 注册文档信息到merge_service
    merge_service._documents[doc_id] = {
        "id": doc_id,
        "name": file.filename,
        "path": str(target_path),
    }

    return {
        "success": True,
        "document_id": doc_id,
        "filename": file.filename,
        "status": "uploaded",
    }


@router.post("/merge/upload-documents-batch")
async def upload_documents_batch(files: List[UploadFile] = File(...)):
    """批量上传文档用于合并"""
    import uuid
    import logging

    logger = logging.getLogger(__name__)

    if not files:
        raise HTTPException(status_code=400, detail="未选择文件")

    results = []

    for file in files:
        try:
            # 验证文件类型
            if not file.filename:
                results.append({
                    "success": False,
                    "filename": "unknown",
                    "error": "文件名不能为空",
                })
                continue

            filename_lower = file.filename.lower()
            if not filename_lower.endswith('.pdf'):
                results.append({
                    "success": False,
                    "filename": file.filename,
                    "error": "只支持PDF格式文件",
                })
                continue

            # 生成文档ID
            doc_id = str(uuid.uuid4())

            # 目标路径
            target_filename = f"{doc_id}.pdf"
            target_path = Path(settings.upload_dir) / target_filename

            # 确保上传目录存在
            target_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存上传的文件
            with open(target_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # 注册文档信息到merge_service
            merge_service._documents[doc_id] = {
                "id": doc_id,
                "name": file.filename,
                "path": str(target_path),
            }

            results.append({
                "success": True,
                "document_id": doc_id,
                "filename": file.filename,
                "status": "uploaded",
            })

            logger.info(f"Uploaded file: {file.filename}, document_id: {doc_id}")

        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {e}")
            results.append({
                "success": False,
                "filename": file.filename if file.filename else "unknown",
                "error": str(e),
            })

    return {
        "success": True,
        "total": len(files),
        "uploaded": sum(1 for r in results if r["success"]),
        "failed": sum(1 for r in results if not r["success"]),
        "results": results,
    }


@router.post("/merge/select-page")
async def select_page(page: SelectedPagePydantic):
    """选择页面添加到拼接队列"""
    service_page = MergeServiceSelectedPage(
        id=page.id,
        document_id=page.document_id,
        page_index=page.page_index,
        original_document_name=page.original_document_name,
        thumbnail=page.thumbnail,
        page_width=page.page_width,
        page_height=page.page_height,
        rotation=page.rotation,
    )

    result = merge_service.select_page(service_page)

    return result


@router.delete("/merge/select-page/{page_id}")
async def deselect_page(page_id: str):
    """取消选择页面"""
    result = merge_service.deselect_page(page_id)

    return result


@router.post("/merge/select-range")
async def select_page_range(document_id: str, start: int, end: int):
    """按范围选择页面"""
    result = await merge_service.select_page_range(document_id, start, end)

    return result


@router.post("/merge/toggle-all/{document_id}")
async def toggle_all_pages(document_id: str):
    """全选/取消全选文档的所有页面"""
    result = await merge_service.toggle_all_pages(document_id)

    return result


@router.post("/merge/reorder")
async def reorder_page(page_id: str, new_index: int):
    """调整拼接队列中页面顺序"""
    result = merge_service.reorder_page(page_id, new_index)

    return result


@router.delete("/merge/queue")
async def clear_queue():
    """清空拼接队列"""
    result = merge_service.clear_queue()

    return result


@router.get("/merge/queue", response_model=List[SelectedPagePydantic])
async def get_queue():
    """获取当前拼接队列"""
    queue = merge_service.get_queue()

    return [_to_pydantic_page(page) for page in queue]


@router.post("/merge/execute", response_model=MergeResultPydantic)
async def merge_documents(config: MergeConfigPydantic):
    """生成合并后的PDF"""
    service_config = _to_service_config(config)
    result = await merge_service.merge_documents(service_config)

    return _to_pydantic_result(result)


@router.get("/merge/preview")
async def preview_merge():
    """预览合并结果"""
    thumbnails = await merge_service.preview_merge()

    return {"thumbnails": thumbnails}


@router.get("/merge/documents/{document_id}/pages")
async def get_document_pages(document_id: str):
    """获取文档的所有页面信息"""
    result = await merge_service.get_document_pages(document_id)

    if result.get("success"):
        return result
    else:
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))


@router.get("/merge/download/{filename}")
async def download_merged_file(filename: str):
    """下载合并后的PDF文件"""
    import logging
    logger = logging.getLogger(__name__)

    # 构建文件路径
    file_path = Path(settings.output_dir) / filename

    # 检查文件是否存在
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="文件不存在")

    # 返回文件
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/pdf",
    )


@router.delete("/merge/documents/{document_id}")
async def delete_document(document_id: str):
    """删除上传的文档"""
    import logging
    logger = logging.getLogger(__name__)

    result = merge_service.delete_document(document_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "删除失败"))

    logger.info(f"Deleted document: {document_id}")
    return result
