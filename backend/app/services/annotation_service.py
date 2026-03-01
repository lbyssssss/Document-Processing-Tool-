# Annotation Service
from typing import List, Optional
from datetime import datetime
import uuid
import json
from pathlib import Path


class Rectangle:
    """矩形区域"""
    def __init__(self, x: float, y: float, width: float, height: float):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class Annotation:
    """批注模型"""
    def __init__(
        self,
        id: str = None,
        document_id: str = None,
        page_index: int = 0,
        position: Rectangle = None,
        content: str = "",
        author: str = "匿名用户",
        color: str = "#FF5722",
        created_at: datetime = None,
        updated_at: datetime = None,
    ):
        self.id = id or str(uuid.uuid4())
        self.document_id = document_id
        self.page_index = page_index
        self.position = position
        self.content = content
        self.author = author
        self.color = color
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "document_id": self.document_id,
            "page_index": self.page_index,
            "position": {
                "x": self.position.x if self.position else 0,
                "y": self.position.y if self.position else 0,
                "width": self.position.width if self.position else 0,
                "height": self.position.height if self.position else 0,
            },
            "content": self.content,
            "author": self.author,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Annotation":
        """从字典创建"""
        position_data = data.get("position", {})
        position = Rectangle(
            x=position_data.get("x", 0),
            y=position_data.get("y", 0),
            width=position_data.get("width", 0),
            height=position_data.get("height", 0),
        )

        return cls(
            id=data.get("id"),
            document_id=data.get("document_id"),
            page_index=data.get("page_index", 0),
            position=position,
            content=data.get("content", ""),
            author=data.get("author", "匿名用户"),
            color=data.get("color", "#FF5722"),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None,
        )


class AnnotationService:
    """批注管理服务"""

    def __init__(self, storage_path: str = None):
        """初始化批注服务

        Args:
            storage_path: 批注存储路径
        """
        self.storage_path = Path(storage_path or "storage/annotations")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._annotations: dict = {}  # document_id -> List[Annotation]

        # 加载已保存的批注
        self.load_from_storage()

    def add(self, annotation: Annotation) -> Annotation:
        """添加批注

        Args:
            annotation: 批注对象

        Returns:
            添加的批注对象
        """
        document_id = annotation.document_id
        if not document_id:
            raise ValueError("批注必须关联一个文档")

        # 初始化文档的批注列表
        if document_id not in self._annotations:
            self._annotations[document_id] = []

        # 添加批注
        self._annotations[document_id].append(annotation)

        # 保存到存储
        self.save_to_storage()

        return annotation

    def update(self, annotation_id: str, updates: dict) -> Optional[Annotation]:
        """更新批注

        Args:
            annotation_id: 批注ID
            updates: 更新的字段

        Returns:
            更新后的批注对象，如果不存在则返回None
        """
        for doc_id, annotations in self._annotations.items():
            for annotation in annotations:
                if annotation.id == annotation_id:
                    # 更新字段
                    for key, value in updates.items():
                        if hasattr(annotation, key):
                            setattr(annotation, key, value)

                    # 更新时间戳
                    annotation.updated_at = datetime.now()

                    # 保存到存储
                    self.save_to_storage()

                    return annotation

        return None

    def remove(self, annotation_id: str) -> bool:
        """删除批注

        Args:
            annotation_id: 批注ID

        Returns:
            是否成功删除
        """
        for doc_id, annotations in self._annotations.items():
            for i, annotation in enumerate(annotations):
                if annotation.id == annotation_id:
                    annotations.pop(i)

                    # 如果文档没有批注了，删除文档条目
                    if not annotations:
                        del self._annotations[doc_id]

                    # 保存到存储
                    self.save_to_storage()

                    return True

        return False

    def list(self, document_id: str) -> List[Annotation]:
        """获取文档批注列表

        Args:
            document_id: 文档ID

        Returns:
            批注列表
        """
        return self._annotations.get(document_id, [])

    def get(self, annotation_id: str) -> Optional[Annotation]:
        """获取单个批注

        Args:
            annotation_id: 批注ID

        Returns:
            批注对象，如果不存在则返回None
        """
        for annotations in self._annotations.values():
            for annotation in annotations:
                if annotation.id == annotation_id:
                    return annotation

        return None

    def save_to_storage(self) -> None:
        """保存到本地存储"""
        try:
            # 转换为可序列化的格式
            data = {}
            for doc_id, annotations in self._annotations.items():
                data[doc_id] = [a.to_dict() for a in annotations]

            # 写入文件
            storage_file = self.storage_path / "annotations.json"
            with open(storage_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"保存批注失败: {e}")

    def load_from_storage(self) -> None:
        """从本地存储加载"""
        try:
            storage_file = self.storage_path / "annotations.json"
            if not storage_file.exists():
                return

            with open(storage_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 转换为Annotation对象
            self._annotations = {}
            for doc_id, annotations_data in data.items():
                self._annotations[doc_id] = [
                    Annotation.from_dict(a) for a in annotations_data
                ]

        except Exception as e:
            print(f"加载批注失败: {e}")
            self._annotations = {}

    def clear_document(self, document_id: str) -> bool:
        """清除文档的所有批注

        Args:
            document_id: 文档ID

        Returns:
            是否成功清除
        """
        if document_id in self._annotations:
            del self._annotations[document_id]
            self.save_to_storage()
            return True

        return False

    def get_all_documents(self) -> List[str]:
        """获取所有有批注的文档ID列表

        Returns:
            文档ID列表
        """
        return list(self._annotations.keys())

    def get_stats(self, document_id: str = None) -> dict:
        """获取批注统计信息

        Args:
            document_id: 文档ID，如果为None则返回全局统计

        Returns:
            统计信息字典
        """
        if document_id:
            annotations = self._annotations.get(document_id, [])
            return {
                "document_id": document_id,
                "count": len(annotations),
                "authors": list(set(a.author for a in annotations)),
            }
        else:
            total_count = sum(len(a) for a in self._annotations.values())
            return {
                "total_documents": len(self._annotations),
                "total_annotations": total_count,
                "authors": list(
                    set(a.author for annotations in self._annotations.values() for a in annotations)
                ),
            }
