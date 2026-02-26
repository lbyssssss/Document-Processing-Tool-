# Images to PDF Conversion
from PIL import Image
from pathlib import Path
from typing import List, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, A3, letter
from reportlab.platypus import SimpleDocTemplate
import io


class ImagesToPDFConverter:
    """图片转PDF转换器"""

    def __init__(self, images: List[Path], output_path: Path, page_size: str = "auto", orientation: str = "keep-original"):
        self.images = images
        self.output_path = output_path
        self.page_size = page_size
        self.orientation = orientation

    def convert(self) -> dict:
        """将多张图片转换为PDF文档"""
        try:
            if not self.images:
                return {
                    "success": False,
                    "error": "没有提供图片文件",
                }

            # 创建PDF文档
            pdf = SimpleDocTemplate(str(self.output_path), pagesize=self._get_page_size())

            # 处理每张图片
            images_processed = []

            for i, image_path in enumerate(self.images):
                result = self._add_image_to_pdf(pdf, image_path, i)
                if result.get("success"):
                    images_processed.append(result)

            return {
                "success": True,
                "output_file": str(self.output_path),
                "images_added": len(images_processed),
                "images": images_processed,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _add_image_to_pdf(self, pdf, image_path: Path, index: int) -> dict:
        """添加单张图片到PDF"""
        try:
            # 打开图片
            img = Image.open(image_path)

            # 获取图片尺寸
            img_width, img_height = img.size

            # 计算适合PDF页面的尺寸
            pdf_width, pdf_height = self._calculate_fit_dimensions(img_width, img_height)

            # 将图片转换为PDF可用格式
            from io import BytesIO
            img_buffer = BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            from reportlab.platypus import Image as RLImage
            pdf_img = RLImage(img_buffer)

            # 计算居中位置
            x = (pdf_width - img_width) / 2
            y = (pdf_height - img_height) / 2

            # 添加图片到PDF
            pdf.drawImage(
                pdf_img,
                x, y,
                width=img_width,
                height=img_height,
                preserveAspectRatio=True,
                mask='auto'
            )

            # 添加分页（除了最后一张）
            if index < len(self.images) - 1:
                pdf.showPage()

            return {
                "success": True,
                "image_name": image_path.name,
                "original_size": f"{img_width}x{img_height}",
                "fitted_size": f"{pdf_width}x{pdf_height}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"添加图片{image_path.name}失败: {str(e)}",
            }

    def _get_page_size(self):
        """获取PDF页面尺寸"""
        if self.page_size == "a4":
            return A4
        elif self.page_size == "a3":
            return A3
        elif self.page_size == "letter":
            return letter
        else:
            return A4  # 默认使用A4

    def _calculate_fit_dimensions(self, img_width: int, img_height: int) -> tuple[int, int]:
        """计算图片适合PDF页面的尺寸"""
        page_size = self._get_page_size()

        # 获取PDF页面尺寸
        if self.orientation == "landscape":
            pdf_width = page_size[1]  # width is at index 1
            pdf_height = page_size[0]  # height is at index 0
        elif self.orientation == "portrait":
            pdf_width = page_size[0]
            pdf_height = page_size[1]
        else:
            # keep-original: 根据图片比例调整
            img_aspect = img_width / img_height
            page_aspect = page_size[0] / page_size[1]

            if img_aspect > page_aspect:
                # 图片更宽，以宽度为基准
                pdf_width = page_size[0]
                pdf_height = int(pdf_width / img_aspect)
            else:
                # 图片更高，以高度为基准
                pdf_height = page_size[1]
                pdf_width = int(pdf_height * img_aspect)

        return (pdf_width, pdf_height)

    def get_images_info(self) -> dict:
        """获取图片信息"""
        try:
            images_info = []

            for image_path in self.images:
                with Image.open(image_path) as img:
                    images_info.append({
                        "name": image_path.name,
                        "width": img.size[0],
                        "height": img.size[1],
                        "format": img.format,
                        "mode": img.mode,
                    })

            return {
                "success": True,
                "images": images_info,
                "total_images": len(images_info),
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
