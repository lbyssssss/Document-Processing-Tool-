# Annotation API
from fastapi import APIRouter

router = APIRouter()


@router.get("/annotation")
async def get_annotations():
    """获取批注列表"""
    return {"annotations": []}


@router.post("/annotation")
async def create_annotation():
    """创建批注"""
    return {"success": True, "message": "批注创建成功"}
