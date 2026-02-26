# Merge API
from fastapi import APIRouter, HTTPException, UploadFile, File
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
    # 生成文档ID
    import uuid
    doc_id = str(uuid.uuid4())

    # 目标路径
    target_filename = f"{doc_id}.pdf"
    target_path = Path(settings.upload_dir) / target_filename

    # 保存文件
    with open(target_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 将文档信息添加到 merge_service 中
    merge_service._documents[doc_id] = {
        "id": doc_id,
        "name": file.filename,
        "path": str(target_path),
    }

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "status": "uploaded",
        "page_count": 0,
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
    try:
        service_config = _to_service_config(config)
        result = await merge_service.merge_documents(service_config)
        return _to_pydantic_result(result)
    except TypeError as e:
        import traceback
        traceback.print_exc()
        return _to_pydantic_result(
            MergeServiceMergeResult(success=False, total_pages=0, error=str(e))
        )


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
        error_msg = result.get("error", "Unknown error")
        # 如果是"文档不存在"的错误，返回404；其他错误返回500
        if "不存在" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        else:
            raise HTTPException(status_code=500, detail=error_msg)


@router.get("/merge/download/{filename}")
async def download_merged_file(filename: str):
    """下载合并后的PDF文件"""
    try:
        from fastapi.responses import FileResponse

        file_path = Path(settings.output_dir) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"文件 {filename} 不存在")

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type='application/pdf'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
