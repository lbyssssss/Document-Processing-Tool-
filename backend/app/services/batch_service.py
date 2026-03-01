# Batch Processing Service
from typing import List, Optional, Dict, Any
from pathlib import Path
from datetime import datetime
import uuid
import asyncio
import shutil

from app.services.conversion_service import (
    ConversionService,
    ConversionOptions,
    ConversionResult,
)


class BatchTask:
    """批量任务"""

    def __init__(
        self,
        task_id: str,
        task_type: str,
        files: List[Path],
        options: Dict[str, Any] = None,
    ):
        self.task_id = task_id
        self.task_type = task_type  # "convert", "annotate", "page_ops"
        self.files = files
        self.options = options or {}
        self.status = "pending"  # pending, running, completed, failed, cancelled
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.results: List[Dict] = []
        self.current_index = 0
        self.total_count = len(files)
        self.success_count = 0
        self.failure_count = 0
        self.warning_count = 0
        self.error_message = None


class BatchService:
    """批量处理服务"""

    def __init__(self, upload_dir: str, output_dir: str):
        """初始化批量处理服务

        Args:
            upload_dir: 上传目录
            output_dir: 输出目录
        """
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化转换服务
        self.conversion_service = ConversionService(upload_dir, output_dir)

        # 存储任务
        self._tasks: Dict[str, BatchTask] = {}

    def create_task(
        self,
        task_type: str,
        files: List[Path],
        options: Dict[str, Any] = None,
    ) -> BatchTask:
        """创建批量任务

        Args:
            task_type: 任务类型
            files: 文件列表
            options: 选项

        Returns:
            创建的任务
        """
        task_id = str(uuid.uuid4())
        task = BatchTask(task_id, task_type, files, options)
        self._tasks[task_id] = task
        return task

    def get_task(self, task_id: str) -> Optional[BatchTask]:
        """获取任务

        Args:
            task_id: 任务ID

        Returns:
            任务对象，不存在则返回None
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> List[BatchTask]:
        """获取所有任务

        Returns:
            任务列表
        """
        return list(self._tasks.values())

    def delete_task(self, task_id: str) -> bool:
        """删除任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功删除
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行批量任务

        Args:
            task_id: 任务ID

        Returns:
            任务执行结果
        """
        task = self._tasks.get(task_id)

        if not task:
            return {
                "success": False,
                "error": f"任务 {task_id} 不存在",
            }

        # 更新任务状态
        task.status = "running"
        task.started_at = datetime.now()
        task.current_index = 0

        try:
            # 根据任务类型执行
            if task.task_type == "convert":
                result = await self._execute_batch_convert(task)
            elif task.task_type == "images_to_pdf":
                result = await self._execute_images_to_pdf(task)
            else:
                result = {
                    "success": False,
                    "error": f"不支持的任务类型: {task.task_type}",
                }

            # 更新任务状态
            if result.get("success"):
                task.status = "completed"
            else:
                task.status = "failed"
                task.error_message = result.get("error", "未知错误")

            task.completed_at = datetime.now()

            return result

        except Exception as e:
            task.status = "failed"
            task.error_message = str(e)
            task.completed_at = datetime.now()

            return {
                "success": False,
                "error": str(e),
            }

    async def _execute_batch_convert(self, task: BatchTask) -> Dict[str, Any]:
        """执行批量转换

        Args:
            task: 批量任务

        Returns:
            执行结果
        """
        target_format = task.options.get("target_format", "pdf")
        conversion_options = ConversionOptions(
            preserve_formatting=task.options.get("preserve_formatting", True),
            quality=task.options.get("quality", 90),
            password=task.options.get("password"),
            include_annotations=task.options.get("include_annotations", False),
            dpi=task.options.get("dpi"),
        )

        results = []

        for i, file_path in enumerate(task.files):
            # 更新进度
            task.current_index = i + 1

            file_result = {
                "file": file_path.name,
                "index": i,
                "status": "processing",
            }

            try:
                # 根据文件扩展名和目标格式选择转换方法
                file_ext = file_path.suffix.lower()

                if file_ext == ".pdf" and target_format == "docx":
                    result = await self.conversion_service.pdf_to_word(
                        file_path, conversion_options
                    )
                elif file_ext in [".doc", ".docx"] and target_format == "pdf":
                    result = await self.conversion_service.word_to_pdf(
                        file_path, conversion_options
                    )
                elif file_ext == ".pdf" and target_format == "xlsx":
                    result = await self.conversion_service.pdf_to_excel(
                        file_path, conversion_options
                    )
                elif file_ext in [".xls", ".xlsx"] and target_format == "pdf":
                    result = await self.conversion_service.excel_to_pdf(
                        file_path, conversion_options
                    )
                elif file_ext == ".pdf" and target_format == "pptx":
                    result = await self.conversion_service.pdf_to_ppt(
                        file_path, conversion_options
                    )
                elif file_ext in [".ppt", ".pptx"] and target_format == "pdf":
                    result = await self.conversion_service.ppt_to_pdf(
                        file_path, conversion_options
                    )
                elif file_ext == ".pdf" and target_format == "images":
                    image_results = await self.conversion_service.pdf_to_images(
                        file_path, conversion_options
                    )
                    result = image_results[0] if image_results else ConversionResult(
                        success=False, output_format="png", error="转换失败"
                    )
                else:
                    result = ConversionResult(
                        success=False,
                        output_format=target_format,
                        error=f"不支持的转换: {file_ext} -> {target_format}",
                    )

                # 更新结果
                if result.success:
                    task.success_count += 1
                    file_result.update({
                        "status": "success",
                        "output_path": result.output_path,
                        "warnings": result.warnings,
                    })
                else:
                    task.failure_count += 1
                    file_result.update({
                        "status": "failed",
                        "error": result.error,
                    })

            except Exception as e:
                task.failure_count += 1
                file_result.update({
                    "status": "failed",
                    "error": str(e),
                })

            results.append(file_result)
            task.results = results

        return {
            "success": True,
            "task_id": task.task_id,
            "total_files": task.total_count,
            "success_count": task.success_count,
            "failure_count": task.failure_count,
            "results": results,
        }

    async def _execute_images_to_pdf(self, task: BatchTask) -> Dict[str, Any]:
        """执行图片转PDF批量任务

        Args:
            task: 批量任务

        Returns:
            执行结果
        """
        options = task.options or {}

        # 获取页面尺寸和方向
        page_size = options.get("page_size", "a4")
        orientation = options.get("orientation", "keep-original")

        conversion_options = ConversionOptions(
            page_size=page_size,
            orientation=orientation,
        )

        results = []

        # 将所有文件分组（按组转换）
        batch_size = options.get("batch_size", 10)
        for batch_start in range(0, len(task.files), batch_size):
            batch_end = min(batch_start + batch_size, len(task.files))
            batch_files = task.files[batch_start:batch_end]

            # 更新进度
            task.current_index = batch_end

            try:
                result = await self.conversion_service.images_to_pdf(
                    batch_files, conversion_options
                )

                batch_result = {
                    "batch_start": batch_start,
                    "batch_end": batch_end,
                    "count": len(batch_files),
                    "status": "success" if result.success else "failed",
                }

                if result.success:
                    task.success_count += len(batch_files)
                    batch_result["output_path"] = result.output_path
                else:
                    task.failure_count += len(batch_files)
                    batch_result["error"] = result.error

                results.append(batch_result)

            except Exception as e:
                task.failure_count += len(batch_files)
                results.append({
                    "batch_start": batch_start,
                    "batch_end": batch_end,
                    "count": len(batch_files),
                    "status": "failed",
                    "error": str(e),
                })

        task.results = results

        return {
            "success": True,
            "task_id": task.task_id,
            "total_files": task.total_count,
            "success_count": task.success_count,
            "failure_count": task.failure_count,
            "results": results,
        }

    def cancel_task(self, task_id: str) -> bool:
        """取消任务

        Args:
            task_id: 任务ID

        Returns:
            是否成功取消
        """
        task = self._tasks.get(task_id)

        if not task or task.status in ["completed", "failed"]:
            return False

        task.status = "cancelled"
        task.completed_at = datetime.now()

        return True

    def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """获取任务进度

        Args:
            task_id: 任务ID

        Returns:
            进度信息
        """
        task = self._tasks.get(task_id)

        if not task:
            return {
                "error": "任务不存在",
            }

        # 计算进度百分比
        progress = (
            (task.current_index / task.total_count * 100)
            if task.total_count > 0
            else 0
        )

        return {
            "task_id": task.task_id,
            "status": task.status,
            "progress": progress,
            "current_index": task.current_index,
            "total_count": task.total_count,
            "success_count": task.success_count,
            "failure_count": task.failure_count,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": task.error_message,
        }

    def clear_old_tasks(self, max_age_hours: int = 24) -> int:
        """清理旧任务

        Args:
            max_age_hours: 最大保留时间（小时）

        Returns:
            清理的任务数量
        """
        now = datetime.now()
        tasks_to_remove = []

        for task_id, task in self._tasks.items():
            if task.completed_at:
                age = (now - task.completed_at).total_seconds() / 3600
                if age > max_age_hours:
                    tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self._tasks[task_id]

        return len(tasks_to_remove)
