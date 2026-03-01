# Images to PPT Conversion
from PIL import Image
from pathlib import Path
from typing import List, Optional
from pptx import Presentation
from pptx.util import Inches, Pt
import io


class ImagesToPPTConverter:
    """图片转PPT转换器"""

    def __init__(self, images: List[Path], output_path: Path, ocr_mode: bool = False):
        self.images = images
        self.output_path = output_path
        self.ocr_mode = ocr_mode

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

            # 如果是OCR模式，提取文字并添加到PPT
            if self.ocr_mode:
                return self._add_ocr_text_to_ppt(prs, image_path, img_width, img_height, index)
            else:
                return self._add_image_to_slide(prs, image_path, img_width, img_height, index)

        except Exception as e:
            return {
                "success": False,
                "error": f"添加图片{image_path.name}失败: {str(e)}",
            }

    def _add_ocr_text_to_ppt(self, prs, image_path: Path, img_width: int, img_height: int, index: int) -> dict:
        """OCR模式：识别图片中的文字并添加到PPT"""
        try:
            from pytesseract import image_to_string, image_to_data
            from pytesseract import Output

            # 添加空白幻灯片
            blank_slide_layout = prs.slide_layouts[6]
            slide = prs.slides.add_slide(blank_slide_layout)

            # 使用 Tesseract OCR 识别文字
            # 获取识别结果包括位置信息
            ocr_data = image_to_data(str(image_path), lang='chi_sim+eng', output_type=Output.DICT)

            # 获取幻灯片尺寸
            slide_width = prs.slide_width
            slide_height = prs.slide_height

            # 如果识别到文字，添加文本框
            if ocr_data and 'text' in ocr_data:
                text_list = ocr_data['text']
                if text_list:
                    # 按垂直位置排序文本块
                    text_lines = []
                    for i, text in enumerate(text_list):
                        if text.strip():
                            # 获取文本块位置（如果有）
                            left = ocr_data['left'][i] if 'left' in ocr_data else 0
                            top = ocr_data['top'][i] if 'top' in ocr_data else 0
                            width = ocr_data['width'][i] if 'width' in ocr_data else slide_width - left
                            height = ocr_data['height'][i] if 'height' in ocr_data else 50

                            # 将图片坐标映射到PPT幻灯片坐标
                            ppt_left = (left / img_width) * slide_width
                            ppt_top = (top / img_height) * slide_height
                            ppt_width = (width / img_width) * slide_width
                            ppt_height = max(Pt(24), (height / img_height) * slide_height)

                            # 设置最小文本框大小
                            ppt_width = max(ppt_width, Inches(2))
                            ppt_height = max(ppt_height, Pt(24))

                            text_lines.append({
                                "text": text.strip(),
                                "left": ppt_left,
                                "top": ppt_top,
                                "width": ppt_width,
                                "height": ppt_height,
                                "original_top": top,
                            })

                    # 按top位置排序文本块（从上到下）
                    text_lines.sort(key=lambda x: x["original_top"])

                    # 添加文本框到幻灯片
                    current_top = Inches(0.5)
                    for text_line in text_lines:
                        text_box = slide.shapes.add_textbox(
                            left=text_line["left"],
                            top=current_top,
                            width=text_line["width"],
                            height=text_line["height"]
                        )

                        text_frame = text_box.text_frame
                        text_frame.word_wrap = True

                        # 根据文本长度动态调整字体大小
                        text_length = len(text_line["text"])
                        if text_length < 10:
                            font_size = Pt(24)
                        elif text_length < 30:
                            font_size = Pt(20)
                        else:
                            font_size = Pt(16)

                        font_size = max(Pt(12), min(font_size, Pt(40)))

                        p = text_frame.paragraphs[0]
                        p.text = text_line["text"]
                        p.font.size = font_size
                        p.font.name = "微软雅黑"

                        current_top += Pt(36)

                    return {
                        "success": True,
                        "image_name": image_path.name,
                        "mode": "OCR",
                        "text_lines": len(text_lines),
                    }

            # 未识别到文字，添加占位文本
            text_box = slide.shapes.add_textbox(
                left=Inches(1),
                top=Inches(2),
                width=Inches(8),
                height=Inches(4)
            )
            text_frame = text_box.text_frame
            text_frame.word_wrap = True
            p = text_frame.paragraphs[0]
            p.text = f"未识别到文字内容\n\n图片: {image_path.name}"
            p.font.size = Pt(14)
            p.font.name = "微软雅黑"

            return {
                "success": True,
                "image_name": image_path.name,
                "mode": "OCR",
                "text_lines": 0,
            }

        except ImportError:
            return {
                "success": False,
                "error": "OCR模块未安装，请运行: apt-get install tesseract-ocr && pip install pytesseract",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"OCR识别失败: {str(e)}",
            }

    def _add_image_to_slide(self, prs, image_path: Path, img_width: int, img_height: int, index: int) -> dict:
        """普通模式：直接添加图片到PPT"""
        try:
            # 计算适合PPT页面的尺寸（使用16:9比例）
            ppt_width, ppt_height = self._calculate_fit_dimensions(img_width, img_height)

            # 将图片转换为PPT可用格式
            img_buffer = io.BytesIO()
            img.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            # 添加空白幻灯片
            blank_slide_layout = prs.slide_layouts[6]
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
                "mode": "IMAGE",
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
