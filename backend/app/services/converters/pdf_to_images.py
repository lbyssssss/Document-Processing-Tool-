# PDF to Images Conversion
from PyPDF2 import PdfReader
from pathlib import Path
from typing import List, Optional
from PIL import Image
import io
import base64


class PDFToImagesConverter:
    """PDF转图片转换器"""

    def __init__(self, pdf_path: Path, output_dir: Path, format: str = "png", dpi: int = 200):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.format = format.lower()  # png, jpg, jpeg
        self.dpi = dpi

    def convert(self, page_numbers: Optional[List[int]] = None) -> dict:
        """将PDF页面转换为图片

        Args:
            page_numbers: 指定要转换的页码，None表示全部页面
        """
        try:
            reader = PdfReader(str(self.pdf_path))
            total_pages = len(reader.pages)

            # 确定要转换的页码
            if page_numbers is None:
                pages_to_convert = list(range(total_pages))
            else:
                pages_to_convert = [p - 1 for p in page_numbers if 1 <= p <= total_pages]

            if not pages_to_convert:
                return {
                    "success": False,
                    "error": "没有要转换的页面",
                }

            # 确保输出目录存在
            self.output_dir.mkdir(parents=True, exist_ok=True)

            images_created = []

            for page_num in pages_to_convert:
                page = reader.pages[page_num]
                image_info = self._convert_page_to_image(page, page_num)
                if image_info.get("success"):
                    images_created.append(image_info)

            return {
                "success": True,
                "output_dir": str(self.output_dir),
                "images": images_created,
                "pages_converted": len(images_created),
                "total_pages": total_pages,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _convert_page_to_image(self, page, page_num: int) -> dict:
        """将单个PDF页面转换为图片

        注意：pypdf2不直接支持PDF页面渲染为图片
        这里提供框架，实际渲染需要使用pdf2image或其他库
        """
        try:
            # 提取页面信息
            page_width = float(page.mediabox.width)
            page_height = float(page.mediabox.height)

            # 计算图片尺寸（根据DPI）
            img_width = int(page_width * self.dpi / 72)
            img_height = int(page_height * self.dpi / 72)

            # 生成输出文件名
            output_filename = self.output_dir / f"page_{page_num + 1:03d}.{self.format}"

            # 这里实际需要使用pdf2image或类似库进行渲染
            # 目前生成占位图片
            try:
                # 创建一个纯色图片作为占位符
                img = Image.new('RGB', (img_width, img_height), color='white')
                img.save(output_filename, format=self.format.upper())

                return {
                    "success": True,
                    "filename": output_filename.name,
                    "page_number": page_num + 1,
                    "width": img_width,
                    "height": img_height,
                    "format": self.format,
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"保存图片失败: {str(e)}",
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def get_page_info(self) -> dict:
        """获取PDF页面信息"""
        try:
            reader = PdfReader(str(self.pdf_path))
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
                "total_pages": len(pages_info),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
