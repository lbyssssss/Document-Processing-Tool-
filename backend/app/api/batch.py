# Batch Processing API
from fastapi import APIRouter

router = APIRouter()


@router.post("/batch/convert")
async def batch_convert():
    """批量转换"""
    return {"success": True, "message": "批量转换成功"}


@router.get("/batch/status/{task_id}")
async def get_batch_status(task_id: str):
    """获取批量任务状态"""
    return {"task_id": task_id, "status": "completed"}
