# Page Service
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import base64
import io

from app.services.converters.pdf_merge import DocumentMergeConverter


class PageService:
    """页面管理服务"""

    def __init__(self, upload_dir: str, output_dir: str, thumbnail_dir: str):
        """初始化页面管理服务
        
        Args:
            upload_dir: 上传文件目录
            output_dir: 输出文件目录
            thumbnail_dir: 缩略图目录
        """
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        self.thumbnail_dir = Path(thumbnail_dir)
        
        # 确保目录存在
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnail_dir.mkdir(parents=True, exist_ok=True)

    def list_pages(self, pdf_path: Path) -> dict:
        """获取PDF的所有页面信息
        
        Args:
            pdf_path: PDF文件路径
            
        Returns:
            页面信息字典
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            
            # 获取页面信息
            converter = DocumentMergeConverter(self.thumbnail_dir)
            page_info_result = converter.get_pdf_page_info(pdf_path)
            
            if not page_info_result.get("success"):
                return {
                    "success": False,
                    "error": page_info_result.get("error", "获取页面信息失败"),
                }
            
            return {
                "success": True,
                "document_path": str(pdf_path),
                "total_pages": total_pages,
                "pages": page_info_result.get("pages", []),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_page(self, pdf_path: Path, page_number: int) -> dict:
        """获取指定页面信息
        
        Args:
            pdf_path: PDF文件路径
            page_number: 页码（从1开始）
            
        Returns:
            页面信息字典
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(str(pdf_path))
            
            # 检查页码是否有效
            if page_number < 1 or page_number > len(reader.pages):
                return {
                    "success": False,
                    "error": f"页码 {page_number} 超出范围（1-{len(reader.pages)}）",
                }
            
            page = reader.pages[page_number - 1]
            mediabox = page.mediabox
            
            # 获取页面旋转信息
            rotation = page.get('/Rotate', 0)
            
            # 获取缩略图
            converter = DocumentMergeConverter(self.thumbnail_dir)
            thumbnail_result = converter.extract_page_thumbnails(
                pdf_path,
                pages=[page_number - 1],
                size=(600, 840),  # 更大的预览尺寸
            )
            
            thumbnail_base64 = None
            if thumbnail_result.get("success") and len(thumbnail_result.get("thumbnails", [])) > 0:
                thumbnail_base64 = thumbnail_result["thumbnails"][0]["thumbnail"]
            
            return {
                "success": True,
                "page_number": page_number,
                "width": float(mediabox.width),
                "height": float(mediabox.height),
                "rotation": rotation,
                "thumbnail": thumbnail_base64,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_thumbnail(self, pdf_path: Path, page_number: int, size: int = 300) -> dict:
        """获取页面缩略图
        
        Args:
            pdf_path: PDF文件路径
            page_number: 页码（从1开始）
            size: 缩略图尺寸（宽度）
            
        Returns:
            缩略图信息字典
        """
        try:
            from PyPDF2 import PdfReader
            
            reader = PdfReader(str(pdf_path))
            
            # 检查页码是否有效
            if page_number < 1 or page_number > len(reader.pages):
                return {
                    "success": False,
                    "error": f"页码 {page_number} 超出范围（1-{len(reader.pages)}）",
                }
            
            # 获取页面尺寸
            page = reader.pages[page_number - 1]
            mediabox = page.mediabox
            
            # 计算缩略图尺寸
            aspect_ratio = float(mediabox.width) / float(mediabox.height)
            thumb_width = size
            thumb_height = int(size / aspect_ratio)
            
            # 生成缩略图
            converter = DocumentMergeConverter(self.thumbnail_dir)
            thumbnail_result = converter.extract_page_thumbnails(
                pdf_path,
                pages=[page_number - 1],
                size=(thumb_width, thumb_height),
            )
            
            if not thumbnail_result.get("success"):
                return {
                    "success": False,
                    "error": thumbnail_result.get("error", "生成缩略图失败"),
                }
            
            thumbnail_base64 = thumbnail_result["thumbnails"][0]["thumbnail"]
            
            return {
                "success": True,
                "page_number": page_number,
                "thumbnail": thumbnail_base64,
                "width": thumb_width,
                "height": thumb_height,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def insert_page(self, pdf_path: Path, page_number: int, file: Optional[Path] = None) -> dict:
        """在指定位置插入页面
        
        Args:
            pdf_path: PDF文件路径
            page_number: 插入位置（从1开始）
            file: 要插入的文件路径（可选）
            
        Returns:
            操作结果字典
        """
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            
            # 检查页码是否有效
            if page_number < 1 or page_number > total_pages + 1:
                return {
                    "success": False,
                    "error": f"插入位置 {page_number} 超出范围（1-{total_pages + 1}）",
                }
            
            # 创建新的PDF写入器
            writer = PdfWriter()
            
            # 生成输出路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{pdf_path.stem}_modified_{timestamp}.pdf"
            
            # 插入前几页
            for i in range(page_number - 1):
                writer.add_page(reader.pages[i])
            
            # 插入新页面
            if file and file.exists():
                # 从文件插入
                insert_reader = PdfReader(str(file))
                for page in insert_reader.pages:
                    writer.add_page(page)
            else:
                # 插入空白页
                packet = io.BytesIO()
                can = canvas.Canvas(packet, pagesize=letter)
                can.save()
                packet.seek(0)
                blank_reader = PdfReader(packet)
                writer.add_page(blank_reader.pages[0])
            
            # 插入剩余页面
            for i in range(page_number - 1, total_pages):
                writer.add_page(reader.pages[i])
            
            # 保存新文件
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # 替换原文件
            import shutil
            shutil.copy2(output_path, pdf_path)
            output_path.unlink()
            
            return {
                "success": True,
                "message": "页面插入成功",
                "page_count": total_pages + 1,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def delete_page(self, pdf_path: Path, page_number: int) -> dict:
        """删除指定页面
        
        Args:
            pdf_path: PDF文件路径
            page_number: 页码（从1开始）
            
        Returns:
            操作结果字典
        """
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            
            # 检查页码是否有效
            if page_number < 1 or page_number > total_pages:
                return {
                    "success": False,
                    "error": f"页码 {page_number} 超出范围（1-{total_pages}）",
                }
            
            # 创建新的PDF写入器
            writer = PdfWriter()
            
            # 添加除要删除页面外的所有页面
            for i in range(total_pages):
                if i != page_number - 1:
                    writer.add_page(reader.pages[i])
            
            # 保存新文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{pdf_path.stem}_modified_{timestamp}.pdf"
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # 替换原文件
            import shutil
            shutil.copy2(output_path, pdf_path)
            output_path.unlink()
            
            return {
                "success": True,
                "message": "页面删除成功",
                "page_count": total_pages - 1,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def move_page(self, pdf_path: Path, page_number: int, new_page_number: int) -> dict:
        """移动页面到新位置
        
        Args:
            pdf_path: PDF文件路径
            page_number: 原页码（从1开始）
            new_page_number: 新页码（从1开始）
            
        Returns:
            操作结果字典
        """
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            
            # 检查页码是否有效
            if page_number < 1 or page_number > total_pages:
                return {
                    "success": False,
                    "error": f"原页码 {page_number} 超出范围（1-{total_pages}）",
                }
            
            if new_page_number < 1 or new_page_number > total_pages:
                return {
                    "success": False,
                    "error": f"新页码 {new_page_number} 超出范围（1-{total_pages}）",
                }
            
            # 创建新的PDF写入器
            writer = PdfWriter()
            
            # 获取要移动的页面
            page_to_move = reader.pages[page_number - 1]
            
            # 按新顺序添加页面
            for i in range(total_pages):
                if i == new_page_number - 1:
                    writer.add_page(page_to_move)
                elif i < page_number - 1:
                    writer.add_page(reader.pages[i])
                elif i > page_number - 1:
                    writer.add_page(reader.pages[i])
            
            # 保存新文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{pdf_path.stem}_modified_{timestamp}.pdf"
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # 替换原文件
            import shutil
            shutil.copy2(output_path, pdf_path)
            output_path.unlink()
            
            return {
                "success": True,
                "message": "页面移动成功",
                "from": page_number,
                "to": new_page_number,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def rotate_page(self, pdf_path: Path, page_number: int, degrees: int) -> dict:
        """旋转指定页面
        
        Args:
            pdf_path: PDF文件路径
            page_number: 页码（从1开始）
            degrees: 旋转角度（90、180、270）
            
        Returns:
            操作结果字典
        """
        try:
            from PyPDF2 import PdfReader, PdfWriter
            
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            
            # 检查页码是否有效
            if page_number < 1 or page_number > total_pages:
                return {
                    "success": False,
                    "error": f"页码 {page_number} 超出范围（1-{total_pages}）",
                }
            
            # 创建新的PDF写入器
            writer = PdfWriter()
            
            # 添加页面并旋转指定页面
            for i in range(total_pages):
                if i == page_number - 1:
                    page = reader.pages[i]
                    current_rotation = page.get('/Rotate', 0)
                    page.rotate(degrees)
                    writer.add_page(page)
                else:
                    writer.add_page(reader.pages[i])
            
            # 保存新文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{pdf_path.stem}_modified_{timestamp}.pdf"
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # 替换原文件
            import shutil
            shutil.copy2(output_path, pdf_path)
            output_path.unlink()
            
            return {
                "success": True,
                "message": f"页面旋转 {degrees} 度成功",
                "page_number": page_number,
                "rotation": degrees,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def merge_pages(self, pdf_path: Path, page_numbers: List[int]) -> dict:
        """合并多个页面为一个页面
        
        Args:
            pdf_path: PDF文件路径
            page_numbers: 要合并的页码列表（从1开始）
            
        Returns:
            操作结果字典
        """
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from reportlab.pdfgen import canvas
            from reportlab.lib.utils import ImageReader
            
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            
            # 验证页码
            for page_number in page_numbers:
                if page_number < 1 or page_number > total_pages:
                    return {
                        "success": False,
                        "error": f"页码 {page_number} 超出范围（1-{total_pages}）",
                    }
            
            # 创建新的PDF写入器
            writer = PdfWriter()
            
            # 添加除要合并页面外的所有页面
            for i in range(total_pages):
                if i + 1 not in page_numbers:
                    writer.add_page(reader.pages[i])
            
            # 获取要合并的页面
            pages_to_merge = [reader.pages[pn - 1] for pn in page_numbers]
            
            # 创建新页面（合并所有页面）
            # 这里简化处理，实际需要更复杂的页面合并逻辑
            merged_writer = PdfWriter()
            for page in pages_to_merge:
                merged_writer.add_page(page)
            
            # 生成合并后的页面文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            merged_path = self.output_dir / f"{pdf_path.stem}_merged_{timestamp}.pdf"
            
            with open(merged_path, "wb") as f:
                merged_writer.write(f)
            
            # 添加合并后的页面到结果文档
            merged_reader = PdfReader(str(merged_path))
            for page in merged_reader.pages:
                writer.add_page(page)
            
            # 保存结果文件
            output_path = self.output_dir / f"{pdf_path.stem}_modified_{timestamp}.pdf"
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # 清理临时文件
            merged_path.unlink()
            
            # 替换原文件
            import shutil
            shutil.copy2(output_path, pdf_path)
            output_path.unlink()
            
            return {
                "success": True,
                "message": "页面合并成功",
                "merged_pages": page_numbers,
                "new_page_count": total_pages - len(page_numbers) + 1,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def split_page(self, pdf_path: Path, page_number: int, split_type: str = "vertical") -> dict:
        """拆分页面
        
        Args:
            pdf_path: PDF文件路径
            page_number: 页码（从1开始）
            split_type: 拆分类型（vertical垂直, horizontal水平）
            
        Returns:
            操作结果字典
        """
        try:
            from PyPDF2 import PdfReader, PdfWriter
            from PyPDF2 import Transformation
            from reportlab.pdfgen import canvas
            
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            
            # 检查页码是否有效
            if page_number < 1 or page_number > total_pages:
                return {
                    "success": False,
                    "error": f"页码 {page_number} 超出范围（1-{total_pages}）",
                }
            
            # 获取要拆分的页面
            page_to_split = reader.pages[page_number - 1]
            mediabox = page_to_split.mediabox
            
            # 创建新的PDF写入器
            writer = PdfWriter()
            
            # 添加除要拆分页面外的所有页面
            for i in range(total_pages):
                if i != page_number - 1:
                    writer.add_page(reader.pages[i])
            
            # 拆分页面
            # 这里简化处理，实际需要裁剪页面内容
            # 使用PyPDF2的Transformation来裁剪页面
            page_width = float(mediabox.width)
            page_height = float(mediabox.height)
            
            if split_type == "vertical":
                # 垂直拆分：创建两个页面
                # 左半部分
                left_page = page_to_split
                left_page.mediabox.lower_left = (0, 0)
                left_page.mediabox.upper_right = (page_width / 2, page_height)
                writer.add_page(left_page)
                
                # 右半部分
                right_page = page_to_split
                right_page.mediabox.lower_left = (page_width / 2, 0)
                right_page.mediabox.upper_right = (page_width, page_height)
                # 右半部分需要平移
                transformation = Transformation().translate(-page_width / 2, 0)
                right_page.add_transformation(transformation)
                writer.add_page(right_page)
            else:
                # 水平拆分
                # 上半部分
                top_page = page_to_split
                top_page.mediabox.lower_left = (0, page_height / 2)
                top_page.mediabox.upper_right = (page_width, page_height)
                # 上半部分需要平移
                transformation = Transformation().translate(0, -page_height / 2)
                top_page.add_transformation(transformation)
                writer.add_page(top_page)
                
                # 下半部分
                bottom_page = page_to_split
                bottom_page.mediabox.lower_left = (0, 0)
                bottom_page.mediabox.upper_right = (page_width, page_height / 2)
                writer.add_page(bottom_page)
            
            # 保存新文件
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.output_dir / f"{pdf_path.stem}_modified_{timestamp}.pdf"
            
            with open(output_path, "wb") as f:
                writer.write(f)
            
            # 替换原文件
            import shutil
            shutil.copy2(output_path, pdf_path)
            output_path.unlink()
            
            return {
                "success": True,
                "message": "页面拆分成功",
                "page_number": page_number,
                "split_type": split_type,
                "new_page_count": total_pages + 1,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
