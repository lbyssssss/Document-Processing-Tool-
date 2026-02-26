# PDF to Word Conversion
from PyPDF2 import PdfReader, PdfWriter
from typing import Optional
from pathlib import Path
import io


class PDFToWordConverter:
    """PDF转Word转换器"""

    def __init__(self, pdf_path: Path, output_path: Path):
        self.pdf_path = pdf_path
        self.output_path = output_path

    def convert(self) -> dict:
        """将PDF转换为Word格式

        注意：pypdf2主要用于PDF处理，PDF到Word的转换需要额外的处理
        这里提供基础框架，实际Word生成需要使用其他库
        """
        try:
            # 读取PDF文件
            reader = PdfReader(str(self.pdf_path))

            # 提取文本内容
            text_content = ""
            for page in reader.pages:
                text_content += page.extract_text()

            # 这里实际需要使用python-docx来创建Word文档
            # 或者使用专门的PDF到Word转换库
            # 目前返回基本信息
            return {
                "success": True,
                "page_count": len(reader.pages),
                "text_extracted": len(text_content) > 0,
                "message": "文本提取成功，Word生成需要额外处理",
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def extract_metadata(self) -> dict:
        """提取PDF元数据"""
        try:
            reader = PdfReader(str(self.pdf_path))
            metadata = reader.metadata

            return {
                "title": metadata.get("/Title", "") if metadata else "",
                "author": metadata.get("/Author", "") if metadata else "",
                "subject": metadata.get("/Subject", "") if metadata else "",
                "creator": metadata.get("/Creator", "") if metadata else "",
                "creation_date": metadata.get("/CreationDate", "") if metadata else "",
            }
        except Exception as e:
            return {
                "error": str(e),
            }
