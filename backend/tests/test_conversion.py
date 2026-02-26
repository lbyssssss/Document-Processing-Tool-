# Conversion Service Tests
import pytest
from app.services.conversion_service import ConversionService, ConversionOptions, ConversionResult
from pathlib import Path


@pytest.fixture
def conversion_service():
    """转换服务fixture"""
    return ConversionService()


def test_conversion_options_defaults(conversion_service):
    """测试转换选项默认值"""
    options = ConversionOptions()
    assert options.preserve_formatting is True
    assert options.quality is None
    assert options.password is None
    assert options.include_annotations is False


def test_conversion_result_success(conversion_service):
    """测试成功转换结果"""
    result = ConversionResult(
        success=True,
        output_path="/test/output.docx",
        output_format="docx",
    )
    assert result.success is True
    assert result.output_path == "/test/output.docx"
    assert result.output_format == "docx"
    assert result.error is None


def test_conversion_result_failure(conversion_service):
    """测试失败转换结果"""
    result = ConversionResult(
        success=False,
        output_format="docx",
        error="Conversion failed",
    )
    assert result.success is False
    assert result.error == "Conversion failed"
    assert result.warnings == []


# TODO: Add actual conversion tests when implemented
