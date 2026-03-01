# Merge Service
from typing import List, Optional
from pathlib import Path
from datetime import datetime
import json

from app.core.config import settings
from app.services.converters.pdf_merge import DocumentMergeConverter


class SelectedPage:
    """已选择的页面"""
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
    """拼接配置"""
    def __init__(
        self,
        page_size: str = "auto",
        orientation: str = "keep-original",
        output_file_name: str = "merged.pdf",
        include_bookmarks: bool = False,
        metadata: Optional[dict] = None,
    ):
        self.page_size = page_size
        self.orientation = orientation
        self.output_file_name = output_file_name
        self.include_bookmarks = include_bookmarks
        self.metadata = metadata


class MergeResult:
    """拼接结果"""
    def __init__(
        self,
        success: bool,
        output_path: Optional[str] = None,
        total_pages: int = 0,
        warnings: Optional[List[str]] = None,
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
        self._documents: dict = {}  # document_id -> document info

    def select_page(self, selected_page: SelectedPage) -> dict:
        """选择页面"""
        self._queue.append(selected_page)

        # 确保文档信息存在
        doc_id = selected_page.document_id
        if doc_id not in self._documents:
            self._documents[doc_id] = {
                "id": doc_id,
                "name": selected_page.original_document_name,
                "path": f"{settings.upload_dir}/{doc_id}.pdf",
            }

        return {"status": "selected", "queue_size": len(self._queue)}

    def deselect_page(self, page_id: str) -> dict:
        """取消选择页面"""
        self._queue = [p for p in self._queue if p.id != page_id]

        return {"status": "deselected", "queue_size": len(self._queue)}

    def select_page_range(
        self,
        document_id: str,
        start_index: int,
        end_index: int,
    ) -> dict:
        """批量选择页面范围

        Args:
            document_id: 文档ID
            start_index: 起始页码（从1开始）
            end_index: 结束页码（包含）
        """
        doc_info = self._documents.get(document_id)
        if not doc_info:
            return {
                "success": False,
                "error": f"文档 {document_id} 不存在",
            }

        try:
            from PyPDF2 import PdfReader

            pdf_path = Path(doc_info["path"])
            reader = PdfReader(str(pdf_path))

            total_pages = len(reader.pages)
            converter = DocumentMergeConverter(Path(settings.thumbnail_dir))

            # 提取所有页面的缩略图
            thumbnails_result = converter.extract_page_thumbnails(
                pdf_path,
                pages=list(range(start_index - 1, end_index)),
                size=(150, 210),  # 缩略图尺寸
            )

            if not thumbnails_result.get("success"):
                return {
                    "success": False,
                    "error": thumbnails_result.get("error"),
                }

            # 添加页面到队列
            pages_added = []
            for i in range(start_index - 1, end_index):
                if i < total_pages:
                    page_info = reader.pages[i]

                    page_id = f"{document_id}_page_{i}"

                    # 生成缩略图数据（base64）
                    thumbnail_data = thumbnails_result["thumbnails"][i]["thumbnail"]

                    selected_page = SelectedPage(
                        id=page_id,
                        document_id=document_id,
                        page_index=i,
                        original_document_name=doc_info["name"],
                        thumbnail=thumbnail_data,
                        page_width=thumbnails_result["thumbnails"][i]["width"],
                        page_height=thumbnails_result["thumbnails"][i]["height"],
                        rotation=0,  # 初始旋转
                    )

                    self._queue.append(selected_page)
                    pages_added.append(i + 1)

            return {
                "success": True,
                "pages_added": len(pages_added),
                "queue_size": len(self._queue),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def toggle_all_pages(self, document_id: str) -> dict:
        """全选/取消全选文档的所有页面"""
        doc_info = self._documents.get(document_id)

        if not doc_info:
            return {
                "success": False,
                "error": f"文档 {document_id} 不存在",
            }

        try:
            from PyPDF2 import PdfReader

            pdf_path = Path(doc_info["path"])
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)

            # 检查是否已经全选
            already_selected = [
                p for p in self._queue
                if p.document_id == document_id
            ]

            if len(already_selected) == total_pages:
                # 如果已全选，则全部取消选择
                self._queue = [p for p in self._queue if p.document_id != document_id]
                action = "deselected"
            else:
                # 否则全选
                converter = DocumentMergeConverter(Path(settings.thumbnail_dir))
                thumbnails_result = converter.extract_page_thumbnails(
                    pdf_path,
                    size=(150, 210),
                )

                if not thumbnails_result.get("success"):
                    return {
                        "success": False,
                        "error": thumbnails_result.get("error"),
                    }

                for i, page in enumerate(reader.pages):
                    page_id = f"{document_id}_page_{i}"
                    thumbnail_data = thumbnails_result["thumbnails"][i]["thumbnail"]

                    selected_page = SelectedPage(
                        id=page_id,
                        document_id=document_id,
                        page_index=i,
                        original_document_name=doc_info["name"],
                        thumbnail=thumbnail_data,
                        page_width=thumbnails_result["thumbnails"][i]["width"],
                        page_height=thumbnails_result["thumbnails"][i]["height"],
                        rotation=0,
                    )

                    self._queue.append(selected_page)

                action = "selected"

            return {
                "success": True,
                "action": action,
                "pages_count": total_pages,
                "queue_size": len(self._queue),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def reorder_page(self, page_id: str, new_index: int) -> dict:
        """调整拼接队列中页面顺序"""
        # 找到页面
        old_index = -1
        for i, page in enumerate(self._queue):
            if page.id == page_id:
                old_index = i
                break

        if old_index == -1:
            return {
                "success": False,
                "error": f"页面 {page_id} 不在队列中",
            }

        if new_index < 0 or new_index >= len(self._queue):
            return {
                "success": False,
                "error": f"新索引 {new_index} 无效",
            }

        # 移动页面
        page = self._queue.pop(old_index)
        self._queue.insert(new_index, page)

        return {
            "success": True,
            "from_index": old_index,
            "to_index": new_index,
        }

    def clear_queue(self) -> dict:
        """清空拼接队列"""
        self._queue = []
        return {"status": "cleared"}

    def delete_document(self, document_id: str) -> dict:
        """删除文档及其相关数据"""
        doc_info = self._documents.get(document_id)
        if not doc_info:
            return {"success": False, "error": "文档不存在"}

        # 删除物理文件
        from pathlib import Path
        import os
        file_path = Path(doc_info["path"])
        if file_path.exists():
            try:
                os.remove(file_path)
            except Exception as e:
                return {"success": False, "error": f"删除文件失败: {str(e)}"}

        # 从文档列表中移除
        del self._documents[document_id]

        # 从队列中移除该文档的所有页面
        self._queue = [p for p in self._queue if p.document_id != document_id]

        return {"success": True, "document_id": document_id}

    def get_queue(self) -> List[SelectedPage]:
        """获取当前拼接队列"""
        return self._queue

    async def merge_documents(self, config: MergeConfig) -> MergeResult:
        """生成合并后的PDF"""
        if not self._queue:
            return MergeResult(
                success=False,
                total_pages=0,
                error="队列为空",
            )

        import logging
        logger = logging.getLogger(__name__)

        try:
            # 按文档ID分组
            doc_pages = {}
            doc_id_to_index = {}  # document_id -> index in pdf_files
            doc_index = 0

            for page in self._queue:
                if page.document_id not in doc_pages:
                    doc_pages[page.document_id] = []
                    doc_id_to_index[page.document_id] = doc_index
                    doc_index += 1
                doc_pages[page.document_id].append(page.page_index)

            # 收集所有PDF文件路径（按出现顺序）
            pdf_files = []
            doc_ids_in_order = list(doc_id_to_index.keys())
            for doc_id in doc_ids_in_order:
                doc_info = self._documents.get(doc_id)
                if doc_info and Path(doc_info["path"]).exists():
                    pdf_files.append(Path(doc_info["path"]))

            if not pdf_files:
                return MergeResult(
                    success=False,
                    total_pages=0,
                    error="没有有效的PDF文件",
                )

            # 按队列顺序排序页面
            sorted_pages = []
            for page in self._queue:
                doc_idx = doc_id_to_index.get(page.document_id, 0)
                sorted_pages.append((doc_idx, page.page_index))

            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path(settings.output_dir) / f"merged_{timestamp}.pdf"

            # 使用合并转换器
            converter = DocumentMergeConverter(output_path)
            result = converter.merge_pdf_pages(
                pdf_files=pdf_files,
                page_indices=sorted_pages,
                page_size=config.page_size,
                orientation=config.orientation,
            )

            if not result.get("success"):
                return MergeResult(
                    success=False,
                    total_pages=0,
                    error=result.get("error", "Unknown error"),
                )

            return MergeResult(
                success=True,
                output_path=str(output_path),
                total_pages=result["pages_merged"],
            )

        except Exception as e:
            import traceback
            logger.error(f"Merge failed: {e}")
            logger.error(f"Traceback:\n{traceback.format_exc()}")
            return MergeResult(
                success=False,
                total_pages=0,
                error=str(e),
            )

    async def preview_merge(self) -> List[str]:
        """预览合并结果

        生成队列缩略图
        """
        thumbnails = []
        for page in self._queue:
            # 使用base64编码的缩略图数据直接返回
            thumbnails.append(page.thumbnail)

        return thumbnails

    async def get_document_pages(self, document_id: str) -> dict:
        """获取文档的所有页面信息"""
        doc_info = self._documents.get(document_id)

        if not doc_info:
            return {
                "success": False,
                "error": f"文档 {document_id} 不存在",
            }

        try:
            from PyPDF2 import PdfReader
            from app.services.converters.pdf_merge import DocumentMergeConverter

            pdf_path = Path(doc_info["path"])
            reader = PdfReader(str(pdf_path))

            # 获取页面信息和缩略图
            converter = DocumentMergeConverter(Path(settings.thumbnail_dir))
            page_info = converter.get_pdf_page_info(pdf_path)

            if not page_info.get("success"):
                return {
                    "success": False,
                    "error": page_info.get("error"),
                }

            pages_data = []
            for i, info in enumerate(page_info["pages"]):
                # 提取页面缩略图
                thumbnails_result = converter.extract_page_thumbnails(
                    pdf_path,
                    pages=[i],
                    size=(300, 420),  # 更大的预览尺寸
                )

                if thumbnails_result.get("success"):
                    # 将bytes转换为base64字符串
                    thumbnail_bytes = thumbnails_result["thumbnails"][0]["thumbnail"]
                    import base64
                    thumbnail_base64 = base64.b64encode(thumbnail_bytes).decode('utf-8')
                else:
                    thumbnail_base64 = None

                pages_data.append({
                    "page_number": info["page_number"],
                    "width": info["width"],
                    "height": info["height"],
                    "rotation": info["rotation"],
                    "thumbnail": thumbnail_base64,
                })

            return {
                "success": True,
                "document_id": document_id,
                "document_name": doc_info["name"],
                "total_pages": page_info["total_pages"],
                "pages": pages_data,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
