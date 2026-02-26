# File Utilities
from pathlib import Path
from typing import Optional
import os


def get_file_extension(filename: str) -> Optional[str]:
    """获取文件扩展名（包含点）"""
    return Path(filename).suffix.lower()


def is_supported_format(filename: str, supported_formats: dict) -> Optional[str]:
    """检查文件格式是否支持，返回格式类型"""
    ext = get_file_extension(filename)
    for format_type, extensions in supported_formats.items():
        if ext in extensions:
            return format_type
    return None


def ensure_directory(directory: str) -> Path:
    """确保目录存在，不存在则创建"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size_human(file_path: Path) -> str:
    """获取人类可读的文件大小"""
    size = file_path.stat().st_size
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除不安全字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename.strip()
