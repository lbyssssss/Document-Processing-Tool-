# Annotation API
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.core.config import settings
from app.services.annotation_service import (
    AnnotationService,
    Annotation as ServiceAnnotation,
    Rectangle as ServiceRectangle,
)

router = APIRouter()

# 初始化批注服务
annotation_service = AnnotationService(
    settings.annotation_dir if hasattr(settings, "annotation_dir") else None
)


class RectanglePydantic(BaseModel):
    """矩形区域"""
    x: float
    y: float
    width: float
    height: float


class AnnotationPydantic(BaseModel):
    """批注模型"""
    id: Optional[str] = None
    document_id: str
    page_index: int
    position: RectanglePydantic
    content: str
    author: str = "匿名用户"
    color: str = "#FF5722"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AnnotationStatsPydantic(BaseModel):
    """批注统计"""
    total_documents: int
    total_annotations: int
    authors: List[str]


class DocumentAnnotationStatsPydantic(BaseModel):
    """文档批注统计"""
    document_id: str
    count: int
    authors: List[str]


def _to_service_annotation(data: AnnotationPydantic) -> ServiceAnnotation:
    """转换为服务层批注对象"""
    position = ServiceRectangle(
        x=data.position.x,
        y=data.position.y,
        width=data.position.width,
        height=data.position.height,
    )

    return ServiceAnnotation(
        id=data.id,
        document_id=data.document_id,
        page_index=data.page_index,
        position=position,
        content=data.content,
        author=data.author,
        color=data.color,
        created_at=data.created_at,
        updated_at=data.updated_at,
    )


def _to_pydantic_annotation(annotation: ServiceAnnotation) -> AnnotationPydantic:
    """转换为API层批注对象"""
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
        created_at=annotation.created_at,
        updated_at=annotation.updated_at,
    )


@router.get("/annotation", response_model=List[AnnotationPydantic])
async def get_annotations(document_id: Optional[str] = None):
    """获取批注列表

    Args:
        document_id: 文档ID，如果为None则返回所有批注

    Returns:
        批注列表
    """
    if document_id:
        # 返回指定文档的批注
        annotations = annotation_service.list(document_id)
        return [_to_pydantic_annotation(a) for a in annotations]
    else:
        # 返回所有批注
        all_annotations = []
        for doc_id in annotation_service.get_all_documents():
            all_annotations.extend(annotation_service.list(doc_id))
        return [_to_pydantic_annotation(a) for a in all_annotations]


@router.get("/annotation/stats", response_model=AnnotationStatsPydantic)
async def get_annotation_stats(document_id: Optional[str] = None):
    """获取批注统计

    Args:
        document_id: 文档ID，如果为None则返回全局统计

    Returns:
        统计信息
    """
    stats = annotation_service.get_stats(document_id)

    if document_id:
        return DocumentAnnotationStatsPydantic(
            document_id=stats["document_id"],
            count=stats["count"],
            authors=stats["authors"],
        )
    else:
        return AnnotationStatsPydantic(
            total_documents=stats["total_documents"],
            total_annotations=stats["total_annotations"],
            authors=stats["authors"],
        )


@router.post("/annotation", response_model=AnnotationPydantic)
async def create_annotation(annotation: AnnotationPydantic):
    """创建批注

    Args:
        annotation: 批注数据

    Returns:
        创建的批注
    """
    try:
        service_annotation = _to_service_annotation(annotation)
        created = annotation_service.add(service_annotation)
        return _to_pydantic_annotation(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/annotation/{annotation_id}", response_model=AnnotationPydantic)
async def get_annotation(annotation_id: str):
    """获取单个批注

    Args:
        annotation_id: 批注ID

    Returns:
        批注对象
    """
    annotation = annotation_service.get(annotation_id)

    if not annotation:
        raise HTTPException(status_code=404, detail="批注不存在")

    return _to_pydantic_annotation(annotation)


@router.put("/annotation/{annotation_id}", response_model=AnnotationPydantic)
async def update_annotation(annotation_id: str, annotation: AnnotationPydantic):
    """更新批注

    Args:
        annotation_id: 批注ID
        annotation: 更新的批注数据

    Returns:
        更新后的批注
    """
    # 构建更新数据
    updates = {}
    if annotation.content is not None:
        updates["content"] = annotation.content
    if annotation.color is not None:
        updates["color"] = annotation.color

    # 执行更新
    updated = annotation_service.update(annotation_id, updates)

    if not updated:
        raise HTTPException(status_code=404, detail="批注不存在")

    return _to_pydantic_annotation(updated)


@router.delete("/annotation/{annotation_id}")
async def delete_annotation(annotation_id: str):
    """删除批注

    Args:
        annotation_id: 批注ID

    Returns:
        操作结果
    """
    success = annotation_service.remove(annotation_id)

    if not success:
        raise HTTPException(status_code=404, detail="批注不存在")

    return {"success": True, "message": "批注删除成功"}


@router.delete("/annotation/document/{document_id}")
async def clear_document_annotations(document_id: str):
    """清除文档的所有批注

    Args:
        document_id: 文档ID

    Returns:
        操作结果
    """
    success = annotation_service.clear_document(document_id)

    return {
        "success": success,
        "message": "文档批注清除成功" if success else "文档不存在或没有批注",
    }
