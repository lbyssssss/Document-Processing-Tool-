# Annotation API
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/annotation", tags=["annotation"])


class Annotation(BaseModel):
    id: str
    page: int
    x: float
    y: float
    width: float
    height: float
    type: str  # text, highlight, freehand, shape
    content: str
    color: str
    created_at: str


class AnnotationList(BaseModel):
    document_id: str
    annotations: List[Annotation]


class AnnotationResponse(BaseModel):
    success: bool
    message: str


# 存储注解的文件路径
_ANNOTATION_FILE = Path(settings.output_dir) / "annotations.json"


def _load_annotations():
    """加载注解"""
    if _ANNOTATION_FILE.exists():
        import json
        with open(_ANNOTATION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"annotations": []}


def _save_annotations(annotations: dict):
    """保存注解"""
    import json
    with open(_ANNOTATION_FILE, "w", encoding="utf-8") as f:
        json.dump(annotations, f)


@router.get("/{document_id}", response_model=AnnotationList)
async def get_annotations(document_id: str):
    """获取文档的所有注解"""
    try:
        all_annotations = _load_annotations()
        document_annotations = all_annotations.get("annotations", {}).get(document_id, [])
        return AnnotationList(document_id=document_id, annotations=document_annotations)

    except Exception as e:
        logger.error(f"获取注解失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}", response_model=AnnotationResponse)
async def add_annotation(document_id: str, annotation: Annotation):
    """添加注解"""
    try:
        all_annotations = _load_annotations()
        document_annotations = all_annotations.get("annotations", {})

        # 生成唯一ID
        import uuid
        annotation_id = str(uuid.uuid4())

        new_annotation = {
            "id": annotation_id,
            "page": annotation.page,
            "x": annotation.x,
            "y": annotation.y,
            "width": annotation.width,
            "height": annotation.height,
            "type": annotation.type,
            "content": annotation.content,
            "color": annotation.color,
            "created_at": annotation.created_at,
        }

        document_annotations[document_id].append(new_annotation)
        all_annotations["annotations"] = document_annotations

        _save_annotations(all_annotations)

        logger.info(f"添加注解: {annotation_id}")

        return AnnotationResponse(success=True, message="注解添加成功")

    except Exception as e:
        logger.error(f"添加注解失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}/{annotation_id}")
async def delete_annotation(document_id: str, annotation_id: str):
    """删除注解"""
    try:
        all_annotations = _load_annotations()
        document_annotations = all_annotations.get("annotations", {}).get(document_id, [])

        # 查找并删除注解
        for i, ann in enumerate(document_annotations):
            if ann["id"] == annotation_id:
                document_annotations.pop(i)
                break

        all_annotations["annotations"] = document_annotations
        _save_annotations(all_annotations)

        logger.info(f"删除注解: {annotation_id}")

        return AnnotationResponse(success=True, message="注解删除成功")

    except Exception as e:
        logger.error(f"删除注解失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
