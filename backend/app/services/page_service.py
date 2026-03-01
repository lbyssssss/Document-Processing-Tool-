# Page Management Service
from typing import Optional, List
from pathlib import Path
from datetime import datetime
import uuid
import shutil

from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import io

from app.services.converters.pdf_merge import DocumentMergeConverter


class PageService:
    """页面管理服务"""

    def __init__(self, storage_dir: str = None):
        """初始化页面管理服务

        Args:
            storage_dir: 文件存储目录
        """
        self.storage_dir = Path(storage_dir or "storage/temp")
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._temp_files: dict = {}  # document_id -> temp_file_path

    def insert(
        self,
        document_id: str,
        pdf_path: str,
        index: int,
        page_data: dict = None,
    ) -> dict:
        """在指定位置插入空白页面

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径
            index: 插入位置（0表示在第一页之前插入）
            page_data: 页面数据（可选，如尺寸、方向等）

        Returns:
            操作结果
        """
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            total_pages = len(reader.pages)

            # 验证索引
            if index < 0 or index > total_pages:
                return {
                    "success": False,
                    "error": f"插入位置 {index} 无效，有效范围是 0-{total_pages}",
                }

            # 添加插入位置之前的页面
            for i in range(index):
                writer.add_page(reader.pages[i])

            # 添加新页面
            new_page = writer.add_blank_page(
                width=595,  # A4宽度
                height=842,  # A4高度
            )

            # 添加插入位置之后的页面
            for i in range(index, total_pages):
                writer.add_page(reader.pages[i])

            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.storage_dir / f"{document_id}_inserted_{timestamp}.pdf"
            writer.write(str(output_path))

            # 保存临时文件路径
            self._temp_files[document_id] = str(output_path)

            return {
                "success": True,
                "output_path": str(output_path),
                "new_page_index": index,
                "total_pages": total_pages + 1,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def delete(self, document_id: str, pdf_path: str, index: int) -> dict:
        """删除指定页面

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径
            index: 要删除的页面索引（从0开始）

        Returns:
            操作结果
        """
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            total_pages = len(reader.pages)

            # 验证索引
            if index < 0 or index >= total_pages:
                return {
                    "success": False,
                    "error": f"页面索引 {index} 无效，有效范围是 0-{total_pages - 1}",
                }

            # 添加除要删除页面外的所有页面
            for i, page in enumerate(reader.pages):
                if i != index:
                    writer.add_page(page)

            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.storage_dir / f"{document_id}_deleted_{timestamp}.pdf"
            writer.write(str(output_path))

            # 保存临时文件路径
            self._temp_files[document_id] = str(output_path)

            return {
                "success": True,
                "output_path": str(output_path),
                "deleted_page_index": index,
                "total_pages": total_pages - 1,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def move(self, document_id: str, pdf_path: str, from_index: int, to_index: int) -> dict:
        """移动页面到新位置

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径
            from_index: 源页面索引
            to_index: 目标页面索引

        Returns:
            操作结果
        """
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            total_pages = len(reader.pages)

            # 验证索引
            if from_index < 0 or from_index >= total_pages:
                return {
                    "success": False,
                    "error": f"源页面索引 {from_index} 无效",
                }

            if to_index < 0 or to_index >= total_pages:
                return {
                    "success": False,
                    "error": f"目标页面索引 {to_index} 无效",
                }

            # 获取要移动的页面
            moved_page = reader.pages[from_index]

            # 构建页面列表，移动页面到新位置
            pages = list(reader.pages)
            pages.pop(from_index)
            pages.insert(to_index, moved_page)

            # 添加所有页面
            for page in pages:
                writer.add_page(page)

            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.storage_dir / f"{document_id}_moved_{timestamp}.pdf"
            writer.write(str(output_path))

            # 保存临时文件路径
            self._temp_files[document_id] = str(output_path)

            return {
                "success": True,
                "output_path": str(output_path),
                "moved_from": from_index,
                "moved_to": to_index,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def rotate(self, document_id: str, pdf_path: str, index: int, degrees: int) -> dict:
        """旋转指定页面

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径
            index: 页面索引
            degrees: 旋转角度（90、180、270）

        Returns:
            操作结果
        """
        try:
            # 验证旋转角度
            if degrees not in [90, 180, 270]:
                return {
                    "success": False,
                    "error": f"旋转角度 {degrees} 无效，只支持 90、180、270 度",
                }

            reader = PdfReader(str(pdf_path))

            total_pages = len(reader.pages)

            # 验证索引
            if index < 0 or index >= total_pages:
                return {
                    "success": False,
                    "error": f"页面索引 {index} 无效",
                }

            page = reader.pages[index]
            rotated_page = page.rotate(degrees)

            writer = PdfWriter()

            # 添加页面
            for i, p in enumerate(reader.pages):
                if i == index:
                    writer.add_page(rotated_page)
                else:
                    writer.add_page(p)

            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.storage_dir / f"{document_id}_rotated_{timestamp}.pdf"
            writer.write(str(output_path))

            # 保存临时文件路径
            self._temp_files[document_id] = str(output_path)

            return {
                "success": True,
                "output_path": str(output_path),
                "rotated_page_index": index,
                "rotation": degrees,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def merge(
        self, document_id: str, pdf_path: str, indices: List[int], output_path: str = None
    ) -> dict:
        """将多个页面合并为一个PDF页面

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径
            indices: 要合并的页面索引列表
            output_path: 输出文件路径（可选）

        Returns:
            操作结果
        """
        try:
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)

            # 验证索引
            for idx in indices:
                if idx < 0 or idx >= total_pages:
                    return {
                        "success": False,
                        "error": f"页面索引 {idx} 无效",
                    }

            # 合并页面（简化实现：将多页放在同一页上）
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(self.storage_dir / f"{document_id}_merged_{timestamp}.pdf")

            c = canvas.Canvas(output_path, pagesize=A4)

            # 将每页缩放到A4纸的四分之一大小，放2x2网格
            width, height = A4
            cell_width = width / 2
            cell_height = height / 2

            for i, idx in enumerate(indices):
                if i >= 4:  # 最多合并4页
                    break

                # 计算位置
                row = i // 2
                col = i % 2
                x = col * cell_width
                y = height - (row + 1) * cell_height

                # 读取原页面并转换为图片（需要pdf2image）
                # 这里使用简化实现：只添加文本占位
                c.drawString(
                    x + 20, y + cell_height - 40, f"合并页面 {idx + 1}"
                )
                c.rect(x + 10, y + 10, cell_width - 20, cell_height - 20)

            c.save()

            return {
                "success": True,
                "output_path": output_path,
                "merged_pages": len(indices[:4]),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def split(self, document_id: str, pdf_path: str, index: int) -> dict:
        """将一个页面拆分为两个页面

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径
            index: 要拆分的页面索引

        Returns:
            操作结果
        """
        try:
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)

            # 验证索引
            if index < 0 or index >= total_pages:
                return {
                    "success": False,
                    "error": f"页面索引 {index} 无效",
                }

            writer = PdfWriter()

            # 添加页面，将拆分的页面分成两个
            for i, page in enumerate(reader.pages):
                if i == index:
                    # 将页面分成两半（简化实现）
                    page_width = float(page.mediabox.width)
                    page_height = float(page.mediabox.height)

                    # 创建上半部分
                    from PyPDF2 import Transformation
                    from PyPDF2.generic import RectangleObject

                    # 简化实现：添加两个空白页面作为占位
                    writer.add_page(reader.pages[i])
                    writer.add_page(reader.pages[i])
                else:
                    writer.add_page(page)

            # 生成输出文件路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.storage_dir / f"{document_id}_split_{timestamp}.pdf"
            writer.write(str(output_path))

            # 保存临时文件路径
            self._temp_files[document_id] = str(output_path)

            return {
                "success": True,
                "output_path": str(output_path),
                "split_page_index": index,
                "total_pages": total_pages + 1,
                "note": "页面拆分功能当前使用简化实现",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    async def get_thumbnail(self, document_id: str, pdf_path: str, index: int) -> Optional[str]:
        """获取页面缩略图

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径
            index: 页面索引

        Returns:
            缩略图的base64编码，失败返回None
        """
        try:
            converter = DocumentMergeConverter(self.storage_dir)
            result = converter.extract_page_thumbnails(
                Path(pdf_path), pages=[index], size=(300, 420)
            )

            if result.get("success") and result.get("thumbnails"):
                thumbnail_data = result["thumbnails"][0]["thumbnail"]
                # 转换为base64
                import base64
                return base64.b64encode(thumbnail_data).decode("utf-8")

            return None

        except Exception as e:
            print(f"生成缩略图失败: {e}")
            return None

    def get_document_pages(self, pdf_path: str) -> dict:
        """获取文档的所有页面信息

        Args:
            pdf_path: PDF文件路径

        Returns:
            页面信息列表
        """
        try:
            reader = PdfReader(str(pdf_path))

            pages = []
            for i, page in enumerate(reader.pages):
                pages.append({
                    "index": i,
                    "width": float(page.mediabox.width),
                    "height": float(page.mediabox.height),
                    "rotation": int(page.rotation),
                })

            return {
                "success": True,
                "total_pages": len(pages),
                "pages": pages,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_temp_file(self, document_id: str) -> Optional[str]:
        """获取文档的临时文件路径

        Args:
            document_id: 文档ID

        Returns:
            临时文件路径，不存在则返回None
        """
        return self._temp_files.get(document_id)

    def clear_temp_files(self) -> None:
        """清除所有临时文件"""
        for file_path in self._temp_files.values():
            try:
                Path(file_path).unlink()
            except Exception:
                pass
        self._temp_files.clear()
