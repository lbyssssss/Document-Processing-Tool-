# File Utilities Tests
import pytest
from app.utils.file_utils import (
    get_file_extension,
    is_supported_format,
    sanitize_filename,
)
from app.utils.format_utils import PageSize, Orientation, get_page_dimensions, detect_page_type


def test_get_file_extension():
    """测试获取文件扩展名"""
    assert get_file_extension("document.pdf") == ".pdf"
    assert get_file_extension("image.JPG") == ".jpg"
    assert get_file_extension("data.xlsx") == ".xlsx"
    assert get_file_extension("no_extension") == ""


def test_is_supported_format():
    """测试支持的格式检测"""
    supported = {
        "pdf": [".pdf"],
        "word": [".doc", ".docx"],
        "excel": [".xls", ".xlsx"],
        "ppt": [".ppt", ".pptx"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    }
    assert is_supported_format("test.pdf", supported) == "pdf"
    assert is_supported_format("test.docx", supported) == "word"
    assert is_supported_format("test.xlsx", supported) == "excel"
    assert is_supported_format("test.pptx", supported) == "ppt"
    assert is_supported_format("test.png", supported) == "image"
    assert is_supported_format("test.xyz", supported) is None


def test_sanitize_filename():
    """测试文件名清理"""
    assert sanitize_filename("test<file>.pdf") == "test_file_.pdf"
    assert sanitize_filename('test:file.pdf') == "test_file.pdf"
    assert sanitize_filename("test\\file.pdf") == "test_file.pdf"
    assert sanitize_filename('test"file.pdf') == "test_file.pdf"
    assert sanitize_filename("test|file.pdf") == "test_file.pdf"
    assert sanitize_filename("test?file.pdf") == "test_file.pdf")
    assert sanitize_filename("test*file.pdf") == "test_file.pdf")


def test_detect_page_type():
    """测试页面类型检测"""
    assert detect_page_type("document.pdf") == "pdf"
    assert detect_page_type("document.docx") == "word"
    assert detect_page_type("document.xlsx") == "excel"
    assert detect_page_type("presentation.pptx") == "ppt"
    assert detect_page_type("image.jpg") == "image"
    assert detect_page_type("unknown.xyz") is None


def test_get_page_dimensions():
    """测试获取页面尺寸"""
    width, height = get_page_dimensions(PageSize.A4, Orientation.PORTRAIT)
    assert width == 595.28
    assert height == 841.89

    width, height = get_page_dimensions(PageSize.A4, Orientation.LANDSCAPE)
    assert width == 841.89
    assert height == 595.28

    width, height = get_page_dimensions(PageSize.AUTO, Orientation.PORTRAIT)
    assert width == 0
    assert height == 0
