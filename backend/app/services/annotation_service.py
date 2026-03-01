# Annotation Service
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import json
import uuid

from app.models.annotation import Annotation, Rectangle


class AnnotationService:
    """批注管理服务"""

    def __init__(self, db_path: str):
        """初始化批注服务
        
        Args:
            db_path: 数据库路径（SQLite文件路径）
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 批注数据字典
        self._annotations: dict = {}  # document_id -> List[Annotation]
        
        # 加载已有数据
        self._load_from_storage()

    def _load_from_storage(self) -> None:
        """从存储加载批注数据"""
        try:
            if self.db_path.exists():
                with open(self.db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for doc_id, annotations_data in data.items():
                        self._annotations[doc_id] = []
                        for ann_data in annotations_data:
                            annotation = Annotation(
                                id=ann_data.get('id'),
                                document_id=ann_data.get('document_id'),
                                page_index=ann_data.get('page_index'),
                                position=Rectangle(
                                    x=ann_data.get('position', {}).get('x', 0),
                                    y=ann_data.get('position', {}).get('y', 0),
                                    width=ann_data.get('position', {}).get('width', 0),
                                    height=ann_data.get('position', {}).get('height', 0),
                                ),
                                content=ann_data.get('content', ''),
                                author=ann_data.get('author', 'anonymous'),
                                color=ann_data.get('color', '#FF5722'),
                            )
                            # 解析时间
                            if ann_data.get('created_at'):
                                annotation.created_at = datetime.fromisoformat(ann_data['created_at'])
                            if ann_data.get('updated_at'):
                                annotation.updated_at = datetime.fromisoformat(ann_data['updated_at'])
                            
                            self._annotations[doc_id].append(annotation)
        except Exception as e:
            print(f"加载批注数据失败: {e}")

    def _save_to_storage(self) -> None:
        """保存批注数据到存储"""
        try:
            data = {}
            for doc_id, annotations in self._annotations.items():
                data[doc_id] = []
                for annotation in annotations:
                    data[doc_id].append({
                        'id': annotation.id,
                        'document_id': annotation.document_id,
                        'page_index': annotation.page_index,
                        'position': {
                            'x': annotation.position.x,
                            'y': annotation.position.y,
                            'width': annotation.position.width,
                            'height': annotation.position.height,
                        },
                        'content': annotation.content,
                        'author': annotation.author,
                        'color': annotation.color,
                        'created_at': annotation.created_at.isoformat() if annotation.created_at else None,
                        'updated_at': annotation.updated_at.isoformat() if annotation.updated_at else None,
                    })
            
            with open(self.db_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存批注数据失败: {e}")

    def add(self, annotation: Annotation) -> Annotation:
        """添加批注
        
        Args:
            annotation: 批注对象
            
        Returns:
            添加后的批注对象
        """
        # 确保有ID
        if not annotation.id:
            annotation.id = str(uuid.uuid4())
        
        # 设置时间
        now = datetime.now()
        annotation.created_at = now
        annotation.updated_at = now
        
        # 添加到文档批注列表
        doc_id = annotation.document_id
        if doc_id not in self._annotations:
            self._annotations[doc_id] = []
        
        self._annotations[doc_id].append(annotation)
        
        # 保存到存储
        self._save_to_storage()
        
        return annotation

    def update(self, annotation_id: str, updates: dict) -> None:
        """更新批注
        
        Args:
            annotation_id: 批注ID
            updates: 更新的字段字典
        """
        # 查找批注
        for doc_id, annotations in self._annotations.items():
            for annotation in annotations:
                if annotation.id == annotation_id:
                    # 更新字段
                    if 'content' in updates:
                        annotation.content = updates['content']
                    if 'position' in updates:
                        annotation.position = updates['position']
                    if 'color' in updates:
                        annotation.color = updates['color']
                    
                    # 更新时间
                    annotation.updated_at = datetime.now()
                    
                    # 保存到存储
                    self._save_to_storage()
                    
                    return

    def remove(self, annotation_id: str) -> None:
        """删除批注
        
        Args:
            annotation_id: 批注ID
        """
        for doc_id, annotations in self._annotations.items():
            # 找到并删除批注
            self._annotations[doc_id] = [
                a for a in annotations if a.id != annotation_id
            ]
            
            # 如果文档没有批注了，删除文档条目
            if not self._annotations[doc_id]:
                del self._annotations[doc_id]
            
            # 保存到存储
            self._save_to_storage()
            
            return

    def list(self, document_id: str) -> List[Annotation]:
        """获取文档的所有批注
        
        Args:
            document_id: 文档ID
            
        Returns:
            批注列表
        """
        return self._annotations.get(document_id, [])

    def get(self, annotation_id: str) -> Optional[Annotation]:
        """获取指定批注
        
        Args:
            annotation_id: 批注ID
            
        Returns:
            批注对象，如果不存在返回None
        """
        for annotations in self._annotations.values():
            for annotation in annotations:
                if annotation.id == annotation_id:
                    return annotation
        return None

    def clear_document(self, document_id: str) -> None:
        """清空文档的所有批注
        
        Args:
            document_id: 文档ID
        """
        if document_id in self._annotations:
            del self._annotations[document_id]
            self._save_to_storage()
