# Document Merge Converter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from typing import List, Optional
from PIL import Image
import io
import base64
from pdf2image import convert_from_bytes


class DocumentMergeConverter:
    """文档拼接转换器"""

    def __init__(self, output_path: Path):
        self.output_path = output_path

    def merge_pdf_pages(
        self,
        pdf_files: List[Path],
        page_indices: List[tuple[int, int]],  # [(doc_index, page_index), ...]
        page_size: str = "auto",
        orientation: str = "keep-original",
    ) -> dict:
        """合并多个PDF页面为一个新PDF

        Args:
            pdf_files: PDF文件路径列表
            page_indices: 要合并的页面索引 [(文档索引, 页面索引), ...]
            page_size: 页面尺寸
            orientation: 页面方向
        """
        try:
            writer = PdfWriter()

            # 创建新PDF文档
            for doc_idx, page_idx in page_indices:
                if doc_idx >= len(pdf_files):
                    return {
                        "success": False,
                        "error": f"文档索引 {doc_idx} 超出范围",
                    }

                pdf_path = pdf_files[doc_idx]
                reader = PdfReader(str(pdf_path))

                if page_idx >= len(reader.pages):
                    return {
                        "success": False,
                        "error": f"页面索引 {page_idx} 超出范围",
                    }

                page = reader.pages[page_idx]

                # 处理页面尺寸和方向
                if orientation == "keep-original":
                    merged_page = page
                elif orientation == "portrait":
                    merged_page = page.rotate(0)
                elif orientation == "landscape":
                    merged_page = page.rotate(90)

                # 如果需要统一页面尺寸，需要添加到标准尺寸的页面
                if page_size != "auto":
                    # TODO: 实现页面尺寸统一逻辑
                    pass

                writer.add_page(merged_page)

            # 写入输出文件
            writer.write(str(self.output_path))

            return {
                "success": True,
                "output_file": str(self.output_path),
                "pages_merged": len(page_indices),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def extract_page_thumbnails(
        self,
        pdf_path: Path,
        pages: Optional[List[int]] = None,
        size: tuple[int, int] = (300, 420),
    ) -> dict:
        """从PDF中提取页面缩略图

        Args:
            pdf_path: PDF文件路径
            pages: 要提取的页码列表，None表示全部页面
            size: 缩略图尺寸（宽度，高度）
        """
        try:
            reader = PdfReader(str(pdf_path))
            thumbnails = []

            # 确定要处理的页码
            page_numbers = list(range(len(reader.pages))) if pages is None else pages

            # 使用 pdf2image 将 PDF 转换为图片，使用更高的 DPI 获得更清晰的图片
            try:
                images = convert_from_bytes(
                    pdf_path.read_bytes(),
                    first_page=page_numbers[0] + 1 if page_numbers else 1,
                    last_page=(page_numbers[-1] + 1) if page_numbers else len(reader.pages),
                    dpi=300,  # 提高 DPI 从 150 到 300
                    thread_count=2,  # 使用多线程加速
                )
            except Exception as e:
                # 如果 pdf2image 失败，返回基本信息
                for page_num in page_numbers:
                    if page_num >= len(reader.pages):
                        continue
                    thumbnails.append({
                        "page_number": page_num + 1,
                        "thumbnail": "",
                        "width": size[0],
                        "height": size[1],
                    })
                return {
                    "success": True,
                    "thumbnails": thumbnails,
                    "total_pages": len(reader.pages),
                }

            # 处理每个页面的缩略图
            for i, page_num in enumerate(page_numbers):
                if page_num >= len(reader.pages):
                    continue

                if i >= len(images):
                    continue

                img = images[i]

                # 使用更高质量的重采样方法缩放图片
                img_copy = img.copy()
                img_copy.thumbnail(size, Image.Resampling.LANCZOS)

                # 转换为 base64，移除 optimize 参数以保持更高质量
                buffer = io.BytesIO()
                img_copy.save(buffer, format='PNG', quality=95)
                img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
                img_data = f"data:image/png;base64,{img_str}"

                thumbnails.append({
                    "page_number": page_num + 1,
                    "thumbnail": img_data,
                    "width": size[0],
                    "height": size[1],
                })

            return {
                "success": True,
                "thumbnails": thumbnails,
                "total_pages": len(reader.pages),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _create_thumbnail(self, page, size: tuple[int, int]) -> Optional[dict]:
        """创建单个页面的缩略图

        注意：pypdf2不直接支持页面渲染为图片
        这里需要使用pdf2image或其他库
        目前返回占位数据
        """
        try:
            # 获取页面尺寸
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            # 计算缩略图尺寸
            width, height = size

            # 返回空字符串（让前端使用默认文档图标）
            return {
                "data": "",
                "width": width,
                "height": height,
                "original_width": int(page_width),
                "original_height": int(page_height),
            }

        except Exception as e:
            return None

    def get_pdf_page_info(self, pdf_path: Path) -> dict:
        """获取PDF的页面信息"""
        try:
            reader = PdfReader(str(pdf_path))

            pages_info = []

            for i, page in enumerate(reader.pages):
                pages_info.append({
                    "page_number": i + 1,
                    "width": float(page.mediabox.width),
                    "height": float(page.mediabox.height),
                    "rotation": int(page.rotation),
                })

            return {
                "success": True,
                "pages": pages_info,
                "total_pages": len(reader.pages),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def split_pdf_pages(
        self,
        pdf_path: Path,
        output_dir: Path,
        split_points: List[int],
    ) -> dict:
        """将PDF按指定位置拆分

        Args:
            pdf_path: PDF文件路径
            output_dir: 输出目录
            split_points: 拆分点（页码列表）
        """
        try:
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)

            if not split_points:
                split_points = [1]

            # 验证拆分点
            split_points = [0] + split_points
            split_points.append(total_pages)

            # 创建拆分后的PDF
            output_files = []

            for i in range(len(split_points) - 1):
                start_page = split_points[i]
                end_page = split_points[i + 1]

                writer = PdfWriter()
                for page_num in range(start_page, end_page):
                    if page_num < total_pages:
                        writer.add_page(reader.pages[page_num])

                # 生成输出文件名
                output_filename = output_dir / f"{pdf_path.stem}_part_{i + 1}.pdf"
                writer.write(str(output_filename))
                output_files.append(str(output_filename))

            return {
                "success": True,
                "output_files": output_files,
                "parts_created": len(output_files),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def rotate_pdf_page(
        self,
        pdf_path: Path,
        page_number: int,
        rotation: int,
        output_path: Path,
    ) -> dict:
        """旋转PDF中的指定页面"""
        try:
            reader = PdfReader(str(pdf_path))

            if page_number < 1 or page_number > len(reader.pages):
                return {
                    "success": False,
                    "error": f"页码 {page_number} 无效",
                }

            page = reader.pages[page_number - 1]

            writer = PdfWriter()
            rotated_page = page.rotate(rotation)
            writer.add_page(rotated_page)
            writer.write(str(output_path))

            return {
                "success": True,
                "output_file": str(output_path),
                "rotation": rotation,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def delete_pdf_page(
        self,
        pdf_path: Path,
        page_number: int,
        output_path: Path,
    ) -> dict:
        """删除PDF中的指定页面"""
        try:
            reader = PdfReader(str(pdf_path))
            writer = PdfWriter()

            if page_number < 1 or page_number > len(reader.pages):
                return {
                    "success": False,
                    "error": f"页码 {page_number} 无效",
                }

            # 添加除指定页面外的所有页面
            for i, page in enumerate(reader.pages):
                if i + 1 != page_number:
                    writer.add_page(page)

            writer.write(str(output_path))

            return {
                "success": True,
                "output_file": str(output_path),
                "pages_kept": len(reader.pages) - 1,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
