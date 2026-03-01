# Document Merge Converter
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path
from typing import List, Optional
from PIL import Image
import io


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
                merged_page = page
                # 注意：PyPDF2 3.0+ 中，rotate() 返回 PageObject
                # 旋转由前端通过 rotation 属性控制，这里保持原样

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
        size: tuple[int, int] = (200, 280),
    ) -> dict:
        """从PDF中提取页面缩略图

        Args:
            pdf_path: PDF文件路径
            pages: 要提取的页码列表，None表示全部页面
            size: 缩略图尺寸（宽度，高度）
        """
        try:
            from pdf2image import convert_from_path

            # 确定要处理的页码（pdf2image 使用 1-based 索引）
            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            page_numbers = list(range(1, total_pages + 1)) if pages is None else [p + 1 for p in pages]

            # 使用 pdf2image 将 PDF 页面转换为图片
            width, height = size

            # 转换指定页面
            images = convert_from_path(
                str(pdf_path),
                dpi=150,
                fmt='png',
                thread_count=1,
                use_cropbox=True,
                strict=False
            )

            thumbnails = []
            for i, img in enumerate(images):
                if i >= len(page_numbers):
                    break

                # 缩放图片到目标尺寸
                img_resized = img.resize((width, height), Image.Resampling.LANCZOS)

                # 转换为字节
                img_byte_arr = io.BytesIO()
                img_resized.save(img_byte_arr, format='PNG')

                # 获取原始页面信息
                page_idx = i  # 0-based index
                page_width = float(reader.pages[page_idx].mediabox.width)
                page_height = float(reader.pages[page_idx].mediabox.height)

                thumbnails.append({
                    "page_number": page_numbers[i],
                    "thumbnail": img_byte_arr.getvalue(),
                    "width": width,
                    "height": height,
                })

            return {
                "success": True,
                "thumbnails": thumbnails,
                "total_pages": total_pages,
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
            }

    def _create_thumbnail(self, page, size: tuple[int, int]) -> Optional[dict]:
        """创建单个页面的缩略图

        使用 pdf2image 将 PDF 页面渲染为图片
        """
        try:
            from pdf2image import convert_from_path

            # 获取页面尺寸
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            # 计算缩略图尺寸
            width, height = size

            # 需要从完整的 PDF 中提取指定页面
            # 由于 pdf2image 无法直接渲染单页，我们需要临时方案
            # 这里使用占位图，因为 pdf2image 需要整个 PDF 文件
            # TODO: 改进为使用 pdf2image 正确渲染指定页面

            # 创建占位图片（白色背景）
            img = Image.new('RGB', (width, height), color='white')

            # 添加页面信息文字
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)

            # 尝试使用默认字体
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
            except:
                font = ImageFont.load_default()

            # 绘制边框和页码
            draw.rectangle([(5, 5), (width-5, height-5)], outline='#ddd', width=2)
            text = f"Page {getattr(page, 'page_number', '?')}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.text(((width - text_width) // 2, (height - text_height) // 2), text, font=font, fill='#666')

            # 转换为字节
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')

            return {
                "data": img_byte_arr.getvalue(),
                "width": width,
                "height": height,
                "original_width": int(page_width),
                "original_height": int(page_height),
            }

        except Exception as e:
            import traceback
            traceback.print_exc()
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
            # PyPDF2 3.0+ 中 rotate() 返回 PageObject
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
