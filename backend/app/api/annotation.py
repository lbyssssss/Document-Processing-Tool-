# Annotation API
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import uuid
import json
import shutil

from app.core.config import settings
from app.services.annotation_service import AnnotationService
from app.models.annotation import Annotation, Rectangle

router = APIRouter()

# 初始化批注服务
annotation_service = AnnotationService(settings.db_url)

# 确保数据目录存在
Path(settings.db_url).parent.parent.mkdir(parents=True, exist_ok=True)


class RectanglePydantic(BaseModel):
    x: float
    y: float
    width: float
    height: float


class AnnotationPydantic(BaseModel):
    id: Optional[str] = None
    document_id: str
    page_index: int
    position: RectanglePydantic
    content: str
    author: str = "anonymous"
    color: str = "#FF5722"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class AnnotationListResponse(BaseModel):
    success: bool
    annotations: List[AnnotationPydantic]
    total: int


def _to_pydantic_annotation(annotation: Annotation) -> AnnotationPydantic:
    """转换服务批注为API批注模型"""
    return AnnotationPydantic(
        id=annotation.id,
        document_id=annotation.document_id,
        page_index=annotation.page_index,
        position=RectanglePydantic(
            x=annotation.position.x,
            y=annotation.position.y,
            width=annotation.position.width,
            height=annotation.position.height,
        ),
        content=annotation.content,
        author=annotation.author,
        color=annotation.color,
        created_at=annotation.created_at.isoformat() if annotation.created_at else None,
        updated_at=annotation.updated_at.isoformat() if annotation.updated_at else None,
    )


def _to_service_annotation(annotation_pydantic: AnnotationPydantic) -> Annotation:
    """转换API批注为服务批注模型"""
    return Annotation(
        id=annotation_pydantic.id or str(uuid.uuid4()),
        document_id=annotation_pydantic.document_id,
        page_index=annotation_pydantic.page_index,
        position=Rectangle(
            x=annotation_pydantic.position.x,
            y=annotation_pydantic.position.y,
            width=annotation_pydantic.position.width,
            height=annotation_pydantic.position.height,
        ),
        content=annotation_pydantic.content,
        author=annotation_pydantic.author,
        color=annotation_pydantic.color,
    )


@router.get("/annotation/{document_id}", response_model=AnnotationListResponse)
async def get_annotations(document_id: str):
    """获取文档的所有批注"""
    try:
        annotations = annotation_service.list(document_id)
        
        return AnnotationListResponse(
            success=True,
            annotations=[_to_pydantic_annotation(a) for a in annotations],
            total=len(annotations),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/annotation/{document_id}/{page_index}")
async def get_page_annotations(document_id: str, page_index: int):
    """获取指定页面的批注"""
    try:
        all_annotations = annotation_service.list(document_id)
        page_annotations = [
            a for a in all_annotations 
            if a.page_index == page_index
        ]
        
        return {
            "success": True,
            "annotations": [_to_pydantic_annotation(a) for a in page_annotations],
            "total": len(page_annotations),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/annotation", response_model=AnnotationPydantic)
async def create_annotation(annotation: AnnotationPydantic):
    """创建批注"""
    try:
        service_annotation = _to_service_annotation(annotation)
        created_annotation = annotation_service.add(service_annotation)
        
        return _to_pydantic_annotation(created_annotation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/annotation/{annotation_id}", response_model=AnnotationPydantic)
async def update_annotation(annotation_id: str, annotation: AnnotationPydantic):
    """更新批注"""
    try:
        # 检查批注是否存在
        existing_annotations = annotation_service.list(annotation.document_id)
        existing = next((a for a in existing_annotations if a.id == annotation_id), None)
        
        if not existing:
            raise HTTPException(status_code=404, detail="批注不存在")
        
        # 准备更新数据
        updates = {
            "content": annotation.content,
            "position": Rectangle(
                x=annotation.position.x,
                y=annotation.position.y,
                width=annotation.position.width,
                height=annotation.position.height,
            ),
            "color": annotation.color,
        }
        
        # 更新批注
        annotation_service.update(annotation_id, updates)
        
        # 获取更新后的批注
        updated_annotations = annotation_service.list(annotation.document_id)
        updated = next((a for a in updated_annotations if a.id == annotation_id), existing)
        
        return _to_pydantic_annotation(updated)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/annotation/{annotation_id}")
async def delete_annotation(annotation_id: str, document_id: str):
    """删除批注"""
    try:
        # 检查批注是否存在
        existing_annotations = annotation_service.list(document_id)
        existing = next((a for a in existing_annotations if a.id == annotation_id), None)
        
        if not existing:
            raise HTTPException(status_code=404, detail="批注不存在")
        
        annotation_service.remove(annotation_id)
        
        return {"success": True, "message": "批注删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/annotation/export/{document_id}")
async def export_annotations(document_id: str, include_annotations: bool = True):
    """导出文档批注"""
    try:
        annotations = annotation_service.list(document_id)
        
        export_data = {
            "document_id": document_id,
            "include_annotations": include_annotations,
            "annotations_count": len(annotations),
            "annotations": [_to_pydantic_annotation(a).model_dump() for a in annotations],
        }
        
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/annotation/batch/{document_id}")
async def batch_create_annotations(document_id: str, annotations: List[AnnotationPydantic]):
    """批量创建批注"""
    try:
        created_annotations = []
        for annotation_pydantic in annotations:
            service_annotation = _to_service_annotation(annotation_pydantic)
            created_annotation = annotation_service.add(service_annotation)
            created_annotations.append(_to_pydantic_annotation(created_annotation))
        
        return {
            "success": True,
            "created_count": len(created_annotations),
            "annotations": created_annotations,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
