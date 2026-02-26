# Merge Service
from typing import List, Optional
from pathlib import Path


class SelectedPage:
    def __init__(
        self,
        id: str,
        document_id: str,
        page_index: int,
        original_document_name: str,
        thumbnail: str,
        page_width: float,
        page_height: float,
        rotation: int,
    ):
        self.id = id
        self.document_id = document_id
        self.page_index = page_index
        self.original_document_name = original_document_name
        self.thumbnail = thumbnail
        self.page_width = page_width
        self.page_height = page_height
        self.rotation = rotation


class MergeConfig:
    def __init__(
        self,
        page_size: str = "auto",
        orientation: str = "keep-original",
        output_file_name: str = "",
        include_bookmarks: bool = False,
        metadata: Optional[dict] = None,
    ):
        self.page_size = page_size
        self.orientation = orientation
        self.output_file_name = output_file_name
        self.include_bookmarks = include_bookmarks
        self.metadata = metadata


class MergeResult:
    def __init__(
        self,
        success: bool,
        output_path: Optional[str] = None,
        total_pages: int = 0,
        warnings: List[str] | None = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.output_path = output_path
        self.total_pages = total_pages
        self.warnings = warnings or []
        self.error = error


class MergeService:
    """文档拼接服务"""

    def __init__(self):
        """初始化拼接服务"""
        self._queue: List[SelectedPage] = []

    def select_page(self, selected_page: SelectedPage) -> None:
        """选择页面"""
        # TODO: Implement page selection
        pass

    def deselect_page(self, page_id: str) -> None:
        """取消选择页面"""
        # TODO: Implement page deselection
        pass

    def select_page_range(
        self, document_id: str, start_index: int, end_index: int
    ) -> None:
        """批量选择页面范围"""
        # TODO: Implement range selection
        pass

    def toggle_all_pages(self, document_id: str) -> None:
        """全选/取消全选文档的所有页面"""
        # TODO: Implement toggle all
        pass

    def reorder_page(self, page_id: str, new_index: int) -> None:
        """调整拼接队列中页面顺序"""
        # TODO: Implement reorder
        pass

    def clear_queue(self) -> None:
        """清空拼接队列"""
        # TODO: Implement clear queue
        pass

    def get_queue(self) -> List[SelectedPage]:
        """获取当前拼接队列"""
        return self._queue

    async def merge_documents(self, config: MergeConfig) -> MergeResult:
        """生成合并后的PDF"""
        # TODO: Implement merge logic using PyPDF2
        return MergeResult(
            success=False,
            total_pages=0,
            error="Not implemented yet",
        )

    async def preview_merge(self) -> List[str]:
        """预览合并结果"""
        # TODO: Implement preview
        return []
