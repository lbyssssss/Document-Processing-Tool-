# Images to PPT Conversion
from PIL import Image
from pathlib import Path
from typing import List
from pptx import Presentation
from pptx.util import Inches
import io


class ImagesToPPTConverter:
    """图片转PPT转换器"""

    def __init__(self, images: List[Path], output_path: Path):
        self.images = images
        self.output_path = output_path

    def convert(self) -> dict:
        """将多张图片转换为PPT文档"""
        try:
            if not self.images:
                return {
                    "success": False,
                    "error": "没有提供图片文件",
                }

            # 创建PPT演示文稿
            prs = Presentation()

            # 处理每张图片
            images_added = []

            for i, image_path in enumerate(self.images):
                result = self._add_image_to_ppt(prs, image_path, i)
                if result.get("success"):
                    images_added.append(result)
                else:
                    return {
                        "success": False,
                        "error": f"添加图片{image_path.name}失败: {result.get('error')}",
                    }

            # 保存PPT文件
            prs.save(str(self.output_path))

            return {
                "success": True,
                "output_file": str(self.output_path),
                "images_added": len(images_added),
                "images": images_added,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def _add_image_to_ppt(self, prs, image_path: Path, index: int) -> dict:
        """添加单张图片到PPT"""
        try:
            # 打开图片
            img = Image.open(image_path)

            # 获取图片尺寸
            img_width, img_height = img.size

            # 计算适合PPT页面的尺寸（使用16:9比例）
            ppt_width, ppt_height = self._calculate_fit_dimensions(img_width, img_height)

            # 将图片转换为PPT可用格式
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            # 添加空白幻灯片
            blank_slide_layout = prs.slide_layouts[6]  # 使用空白布局
            slide = prs.slides.add_slide(blank_slide_layout)

            # 添加图片到幻灯片
            slide.shapes.add_picture(
                img_buffer,
                left=Inches(0),
                top=Inches(0),
                width=Inches(ppt_width),
                height=Inches(ppt_height)
            )

            return {
                "success": True,
                "image_name": image_path.name,
                "original_size": f"{img_width}x{img_height}",
                "fitted_size": f"{ppt_width}x{ppt_height}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"添加图片{image_path.name}失败: {str(e)}",
            }

    def _calculate_fit_dimensions(self, img_width: int, img_height: int) -> tuple[float, float]:
        """计算图片适合PPT幻灯片的尺寸"""
        # PPT标准幻灯片比例 16:9
        ppt_aspect = 16 / 9
        img_aspect = img_width / img_height

        # 使用固定尺寸（10英寸宽）
        base_width = 10

        if img_aspect > ppt_aspect:
            # 图片更宽，以宽度为基准
            ppt_width = base_width
            ppt_height = base_width / img_aspect
        else:
            # 图片更高，以高度为基准
            ppt_height = base_width / ppt_aspect
            ppt_width = ppt_height * img_aspect

        return (ppt_width, ppt_height)

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
