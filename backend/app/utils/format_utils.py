# Format Utilities
from enum import Enum
from typing import Optional


class PageSize(str, Enum):
    """页面尺寸标准"""
    A4 = "A4"
    A3 = "A3"
    LETTER = "Letter"
    AUTO = "auto"


class Orientation(str, Enum):
    """页面方向"""
    PORTRAIT = "portrait"
    LANDSCAPE = "landscape"
    KEEP_ORIGINAL = "keep-original"


def get_page_dimensions(page_size: PageSize, orientation: Orientation) -> tuple[float, float]:
    """获取页面尺寸（宽度，高度）"""
    # A4 size in points
    a4_dimensions = (595.28, 841.89)  # portrait
    a3_dimensions = (841.89, 1190.55)
    letter_dimensions = (612, 792)

    dimensions_map = {
        PageSize.A4: a4_dimensions,
        PageSize.A3: a3_dimensions,
        PageSize.LETTER: letter_dimensions,
    }

    if page_size == PageSize.AUTO:
        return (0, 0)

    width, height = dimensions_map[page_size]

    if orientation == Orientation.LANDSCAPE:
        width, height = height, width

    return (width, height)


def detect_page_type(filename: str) -> Optional[str]:
    """根据文件名检测文档类型"""
    ext = filename.lower()
    if ext.endswith(".pdf"):
        return "pdf"
    elif ext in [".doc", ".docx"]:
        return "word"
    elif ext in [".xls", ".xlsx"]:
        return "excel"
    elif ext in [".ppt", ".pptx"]:
        return "ppt"
    elif ext in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
        return "image"
    return None
