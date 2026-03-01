# Batch Processing API
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import shutil
import uuid

from app.core.config import settings
from app.services.batch_service import BatchService

router = APIRouter()

# 初始化批量处理服务
batch_service = BatchService(settings.upload_dir, settings.output_dir)


class BatchConvertRequestPydantic(BaseModel):
    """批量转换请求"""
    task_type: str = "convert"
    target_format: str = "pdf"
    preserve_formatting: bool = True
    quality: Optional[int] = None
    dpi: Optional[int] = None
    password: Optional[str] = None
    include_annotations: bool = False


class ImagesToPdfRequestPydantic(BaseModel):
    """图片转PDF请求"""
    task_type: str = "images_to_pdf"
    page_size: str = "a4"
    orientation: str = "keep-original"
    batch_size: int = 10


class FileResultPydantic(BaseModel):
    """文件处理结果"""
    file: str
    index: int
    status: str
    output_path: Optional[str] = None
    error: Optional[str] = None
    warnings: Optional[List[str]] = None


class BatchTaskStatusPydantic(BaseModel):
    """批量任务状态"""
    task_id: str
    status: str
    progress: float
    current_index: int
    total_count: int
    success_count: int
    failure_count: int
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None


class BatchResultPydantic(BaseModel):
    """批量处理结果"""
    success: bool
    task_id: str
    total_files: int
    success_count: int
    failure_count: int
    results: Optional[List[dict]] = None
    error: Optional[str] = None


def _save_upload_file(file: UploadFile) -> Path:
    """保存上传的文件"""
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    filename = f"{file_id}{file_ext}"
    file_path = Path(settings.upload_dir) / filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


@router.post("/batch/convert", response_model=BatchResultPydantic)
async def batch_convert(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    request: Optional[BatchConvertRequestPydantic] = None,
):
    """批量转换文档

    Args:
        files: 要转换的文件列表
        request: 转换选项

    Returns:
        批量转换结果
    """
    # 保存上传的文件
    saved_files = []
    for file in files:
        file_path = _save_upload_file(file)
        saved_files.append(file_path)

    # 创建任务
    options = {}
    if request:
        options = {
            "target_format": request.target_format,
            "preserve_formatting": request.preserve_formatting,
            "quality": request.quality,
            "dpi": request.dpi,
            "password": request.password,
            "include_annotations": request.include_annotations,
        }

    task = batch_service.create_task("convert", saved_files, options)

    # 后台执行任务
    background_tasks.add_task(batch_service.execute_task, task.task_id)

    return BatchResultPydantic(
        success=True,
        task_id=task.task_id,
        total_files=len(saved_files),
        success_count=0,
        failure_count=0,
    )


@router.post("/batch/images-to-pdf", response_model=BatchResultPydantic)
async def batch_images_to_pdf(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    request: Optional[ImagesToPdfRequestPydantic] = None,
):
    """批量图片转PDF

    Args:
        files: 要转换的图片文件列表
        request: 转换选项

    Returns:
        批量转换结果
    """
    # 验证文件类型
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    for file in files:
        if Path(file.filename).suffix.lower() not in image_extensions:
            return BatchResultPydantic(
                success=False,
                task_id="",
                total_files=0,
                success_count=0,
                failure_count=0,
                error=f"不支持的文件类型: {file.filename}",
            )

    # 保存上传的文件
    saved_files = []
    for file in files:
        file_path = _save_upload_file(file)
        saved_files.append(file_path)

    # 创建任务
    options = {}
    if request:
        options = {
            "page_size": request.page_size,
            "orientation": request.orientation,
            "batch_size": request.batch_size,
        }

    task = batch_service.create_task("images_to_pdf", saved_files, options)

    # 后台执行任务
    background_tasks.add_task(batch_service.execute_task, task.task_id)

    return BatchResultPydantic(
        success=True,
        task_id=task.task_id,
        total_files=len(saved_files),
        success_count=0,
        failure_count=0,
    )


@router.get("/batch/status/{task_id}", response_model=BatchTaskStatusPydantic)
async def get_batch_status(task_id: str):
    """获取批量任务状态

    Args:
        task_id: 任务ID

    Returns:
        任务状态
    """
    task = batch_service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return batch_service.get_task_progress(task_id)


@router.get("/batch/result/{task_id}")
async def get_batch_result(task_id: str):
    """获取批量任务结果

    Args:
        task_id: 任务ID

    Returns:
        任务结果详情
    """
    task = batch_service.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in ["completed", "failed"]:
        return {
            "task_id": task_id,
            "status": task.status,
            "message": "任务尚未完成",
        }

    return {
        "task_id": task_id,
        "status": task.status,
        "total_files": task.total_count,
        "success_count": task.success_count,
        "failure_count": task.failure_count,
        "results": task.results,
        "error_message": task.error_message,
    }


@router.delete("/batch/task/{task_id}")
async def cancel_batch_task(task_id: str):
    """取消批量任务

    Args:
        task_id: 任务ID

    Returns:
        操作结果
    """
    success = batch_service.cancel_task(task_id)

    if not success:
        raise HTTPException(status_code=400, detail="无法取消该任务")

    return {
        "success": True,
        "message": "任务已取消",
    }


@router.get("/batch/tasks", response_model=List[BatchTaskStatusPydantic])
async def list_batch_tasks():
    """获取所有批量任务列表

    Returns:
        任务列表
    """
    tasks = batch_service.get_all_tasks()

    return [batch_service.get_task_progress(task.task_id) for task in tasks]


@router.post("/batch/cleanup")
async def cleanup_old_tasks(max_age_hours: int = 24):
    """清理旧任务

    Args:
        max_age_hours: 最大保留时间（小时）

    Returns:
        清理结果
    """
    count = batch_service.clear_old_tasks(max_age_hours)

    return {
        "success": True,
        "cleaned_count": count,
    }

