# Batch Processing API
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
from pathlib import Path
import uuid
import shutil
import asyncio

from app.core.config import settings
from app.services.conversion_service import ConversionService, ConversionOptions
from app.services.conversion_service import ConversionResult

router = APIRouter()

# 初始化转换服务
conversion_service = ConversionService(
    upload_dir=settings.upload_dir,
    output_dir=settings.output_dir,
)

# 批量任务存储
batch_tasks: Dict[str, dict] = {}


class BatchTaskRequest(BaseModel):
    """批量任务请求"""
    operation: str  # "convert", "merge", "annotate"
    files: List[str]  # 文件ID列表
    parameters: Optional[dict] = None


class BatchTaskResponse(BaseModel):
    """批量任务响应"""
    task_id: str
    status: str  # "pending", "running", "completed", "failed"
    total_files: int
    completed_files: int = 0
    failed_files: int = 0
    results: List[dict] = []
    errors: List[str] = []


class BatchConversionRequest(BaseModel):
    """批量转换请求"""
    target_format: str  # "pdf", "word", "excel", "ppt", "image"
    preserve_formatting: bool = True
    quality: Optional[int] = None
    dpi: Optional[int] = None


class BatchConversionResult(BaseModel):
    """批量转换结果"""
    success: bool
    total_files: int
    successful_files: int
    failed_files: int
    results: List[dict] = []
    errors: List[str] = []
    download_url: Optional[str] = None


async def _save_upload_file(file: UploadFile) -> Path:
    """保存上传的文件"""
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    filename = f"{file_id}{file_ext}"
    file_path = Path(settings.upload_dir) / filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


@router.post("/batch/upload")
async def batch_upload(files: List[UploadFile] = File(...)):
    """批量上传文件"""
    try:
        uploaded_files = []
        for file in files:
            file_path = await _save_upload_file(file)
            uploaded_files.append({
                "file_id": file_path.stem,
                "filename": file.filename,
                "file_path": str(file_path),
                "size": file_path.stat().st_size,
            })
        
        return {
            "success": True,
            "total_files": len(uploaded_files),
            "files": uploaded_files,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/convert", response_model=BatchTaskResponse)
async def batch_convert(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    target_format: str = "pdf",
    preserve_formatting: bool = True,
    quality: Optional[int] = None,
    dpi: Optional[int] = None,
):
    """批量转换文档
    
    Args:
        files: 要转换的文件列表
        target_format: 目标格式
        preserve_formatting: 是否保持格式
        quality: 输出质量
        dpi: DPI设置（用于图片转换）
    """
    try:
        # 创建任务ID
        task_id = str(uuid.uuid4())
        
        # 保存文件
        saved_files = []
        for file in files:
            file_path = await _save_upload_file(file)
            saved_files.append(file_path)
        
        # 初始化任务
        batch_tasks[task_id] = {
            "task_id": task_id,
            "status": "pending",
            "total_files": len(saved_files),
            "completed_files": 0,
            "failed_files": 0,
            "results": [],
            "errors": [],
        }
        
        # 在后台执行批量转换
        background_tasks.add_task(
            _execute_batch_conversion,
            task_id,
            saved_files,
            target_format,
            preserve_formatting,
            quality,
            dpi,
        )
        
        return BatchTaskResponse(**batch_tasks[task_id])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/status/{task_id}", response_model=BatchTaskResponse)
async def get_batch_status(task_id: str):
    """获取批量任务状态"""
    if task_id not in batch_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return BatchTaskResponse(**batch_tasks[task_id])


@router.post("/batch/cancel/{task_id}")
async def cancel_batch_task(task_id: str):
    """取消批量任务"""
    if task_id not in batch_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    task = batch_tasks[task_id]
    if task["status"] in ["completed", "failed"]:
        raise HTTPException(status_code=400, detail="任务已完成，无法取消")
    
    task["status"] = "cancelled"
    
    return {"success": True, "message": "任务已取消"}


@router.delete("/batch/task/{task_id}")
async def delete_batch_task(task_id: str):
    """删除批量任务"""
    if task_id in batch_tasks:
        del batch_tasks[task_id]
    
    return {"success": True, "message": "任务已删除"}


@router.get("/batch/tasks")
async def list_batch_tasks():
    """列出所有批量任务"""
    return {
        "total_tasks": len(batch_tasks),
        "tasks": [
            {
                "task_id": task_id,
                "status": task["status"],
                "total_files": task["total_files"],
                "completed_files": task["completed_files"],
                "failed_files": task["failed_files"],
            }
            for task_id, task in batch_tasks.items()
        ],
    }


@router.post("/batch/merge")
async def batch_merge_files(files: List[UploadFile] = File(...)):
    """批量合并文件"""
    try:
        # 保存文件
        saved_files = []
        for file in files:
            if file.filename.lower().endswith('.pdf'):
                file_path = await _save_upload_file(file)
                saved_files.append(file_path)
        
        if len(saved_files) < 2:
            raise HTTPException(status_code=400, detail="至少需要2个PDF文件进行合并")
        
        # 执行合并
        from app.services.converters.pdf_merge import DocumentMergeConverter
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = Path(settings.output_dir) / f"batch_merged_{timestamp}.pdf"
        
        converter = DocumentMergeConverter(output_path)
        result = converter.merge_pdf_files(saved_files)
        
        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error"))
        
        return {
            "success": True,
            "message": "文件合并成功",
            "output_path": str(output_path),
            "total_pages": result["pages_merged"],
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_batch_conversion(
    task_id: str,
    files: List[Path],
    target_format: str,
    preserve_formatting: bool,
    quality: Optional[int],
    dpi: Optional[int],
):
    """执行批量转换（后台任务）"""
    task = batch_tasks[task_id]
    task["status"] = "running"
    
    try:
        for i, file_path in enumerate(files):
            try:
                # 准备转换选项
                options = ConversionOptions(
                    preserve_formatting=preserve_formatting,
                    quality=quality,
                    dpi=dpi,
                )
                
                # 根据文件扩展名和目标格式选择转换方法
                file_ext = file_path.suffix.lower()
                result: ConversionResult = None
                
                if target_format == "pdf":
                    if file_ext in [".doc", ".docx"]:
                        result = await conversion_service.word_to_pdf(file_path, options)
                    elif file_ext in [".xls", ".xlsx"]:
                        result = await conversion_service.excel_to_pdf(file_path, options)
                    elif file_ext in [".ppt", ".pptx"]:
                        result = await conversion_service.ppt_to_pdf(file_path, options)
                    elif file_ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                        result = await conversion_service.images_to_pdf([file_path], options)
                    else:
                        raise Exception(f"不支持的文件格式: {file_ext}")
                
                elif target_format == "word":
                    if file_ext == ".pdf":
                        result = await conversion_service.pdf_to_word(file_path, options)
                    else:
                        raise Exception(f"只有PDF可以转换为Word")
                
                elif target_format == "excel":
                    if file_ext == ".pdf":
                        result = await conversion_service.pdf_to_excel(file_path, options)
                    else:
                        raise Exception(f"只有PDF可以转换为Excel")
                
                elif target_format == "ppt":
                    if file_ext == ".pdf":
                        result = await conversion_service.pdf_to_ppt(file_path, options)
                    else:
                        raise Exception(f"只有PDF可以转换为PPT")
                
                elif target_format == "image":
                    if file_ext == ".pdf":
                        results = await conversion_service.pdf_to_images(file_path, options)
                        result = results[0] if results else ConversionResult(success=False, error="转换失败")
                    else:
                        raise Exception(f"只有PDF可以转换为图片")
                
                else:
                    raise Exception(f"不支持的目标格式: {target_format}")
                
                # 记录结果
                if result.success:
                    task["completed_files"] += 1
                    task["results"].append({
                        "filename": file_path.name,
                        "success": True,
                        "output_path": result.output_path,
                        "output_format": result.output_format,
                        "warnings": result.warnings,
                    })
                else:
                    task["failed_files"] += 1
                    task["errors"].append({
                        "filename": file_path.name,
                        "error": result.error,
                    })
                
                # 稍微延迟，避免资源占用过高
                await asyncio.sleep(0.1)
            
            except Exception as e:
                task["failed_files"] += 1
                task["errors"].append({
                    "filename": file_path.name,
                    "error": str(e),
                })
        
        # 标记任务完成
        if task["failed_files"] == 0:
            task["status"] = "completed"
        elif task["completed_files"] > 0:
            task["status"] = "completed_with_errors"
        else:
            task["status"] = "failed"
    
    except Exception as e:
        task["status"] = "failed"
        task["errors"].append({
            "error": f"批量转换任务失败: {str(e)}",
        })


# 导入datetime
from datetime import datetime
