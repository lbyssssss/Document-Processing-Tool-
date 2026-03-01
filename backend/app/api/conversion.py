# Conversion API
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import shutil
import logging

from app.core.config import settings
from app.services.conversion_service import ConversionService, ConversionOptions, ConversionResult

router = APIRouter()
logger = logging.getLogger(__name__)

# 初始化转换服务
conversion_service = ConversionService(
    upload_dir=settings.upload_dir,
    output_dir=settings.output_dir,
)

# 确保目录存在
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
Path(settings.output_dir).mkdir(parents=True, exist_ok=True)


class ConversionOptionsPydantic(BaseModel):
    preserve_formatting: bool = True
    quality: Optional[int] = None
    password: Optional[str] = None
    include_annotations: bool = False
    dpi: Optional[int] = None
    page_size: Optional[str] = None
    orientation: Optional[str] = None
    ocr_mode: bool = False


class ConversionResultPydantic(BaseModel):
    success: bool
    output_path: Optional[str] = None
    output_format: str
    warnings: List[str] = []
    error: Optional[str] = None


async def _save_upload_file(file: UploadFile) -> Path:
    """保存上传的文件"""
    import uuid
    file_id = str(uuid.uuid4())
    file_ext = Path(file.filename).suffix
    filename = f"{file_id}{file_ext}"
    file_path = Path(settings.upload_dir) / filename

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return file_path


def _convert_service_result(service_result: ConversionResult) -> ConversionResultPydantic:
    """转换服务结果为API结果"""
    return ConversionResultPydantic(
        success=service_result.success,
        output_path=service_result.output_path,
        output_format=service_result.output_format,
        warnings=service_result.warnings,
        error=service_result.error,
    )


@router.post("/conversion/pdf-to-word", response_model=ConversionResultPydantic)
async def pdf_to_word(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """PDF转Word"""
    try:
        file_path = await _save_upload_file(file)
        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else None,
            password=options.password if options else None,
            include_annotations=options.include_annotations if options else False,
        )

        result = await conversion_service.pdf_to_word(file_path, service_options)

        return _convert_service_result(result)

    except Exception as e:
        return ConversionResultPydantic(
            success=False,
            output_format="docx",
            error=str(e),
        )


@router.post("/conversion/word-to-pdf", response_model=ConversionResultPydantic)
async def word_to_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """Word转PDF"""
    try:
        file_path = await _save_upload_file(file)
        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else None,
            password=options.password if options else None,
            include_annotations=options.include_annotations if options else False,
        )

        result = await conversion_service.word_to_pdf(file_path, service_options)

        return _convert_service_result(result)

    except Exception as e:
        return ConversionResultPydantic(
            success=False,
            output_format="pdf",
            error=str(e),
        )


@router.post("/conversion/pdf-to-excel", response_model=ConversionResultPydantic)
async def pdf_to_excel(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """PDF转Excel"""
    try:
        file_path = await _save_upload_file(file)
        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else None,
            password=options.password if options else None,
            include_annotations=options.include_annotations if options else False,
        )

        result = await conversion_service.pdf_to_excel(file_path, service_options)

        return _convert_service_result(result)

    except Exception as e:
        return ConversionResultPydantic(
            success=False,
            output_format="xlsx",
            error=str(e),
        )


@router.post("/conversion/excel-to-pdf", response_model=ConversionResultPydantic)
async def excel_to_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """Excel转PDF"""
    try:
        file_path = await _save_upload_file(file)
        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else None,
            password=options.password if options else None,
            include_annotations=options.include_annotations if options else False,
        )

        result = await conversion_service.excel_to_pdf(file_path, service_options)

        return _convert_service_result(result)

    except Exception as e:
        return ConversionResultPydantic(
            success=False,
            output_format="pdf",
            error=str(e),
        )


@router.post("/conversion/pdf-to-ppt", response_model=ConversionResultPydantic)
async def pdf_to_ppt(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """PDF转PPT"""
    try:
        file_path = await _save_upload_file(file)
        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else None,
            password=options.password if options else None,
            include_annotations=options.include_annotations if options else False,
        )

        result = await conversion_service.pdf_to_ppt(file_path, service_options)

        return _convert_service_result(result)

    except Exception as e:
        return ConversionResultPydantic(
            success=False,
            output_format="pptx",
            error=str(e),
        )


@router.post("/conversion/ppt-to-pdf", response_model=ConversionResultPydantic)
async def ppt_to_pdf(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """PPT转PDF"""
    try:
        file_path = await _save_upload_file(file)
        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else None,
            password=options.password if options else None,
            include_annotations=options.include_annotations if options else False,
        )

        result = await conversion_service.ppt_to_pdf(file_path, service_options)

        return _convert_service_result(result)

    except Exception as e:
        return ConversionResultPydantic(
            success=False,
            output_format="pdf",
            error=str(e),
        )


@router.post("/conversion/pdf-to-images", response_model=List[ConversionResultPydantic])
async def pdf_to_images(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """PDF转图片"""
    try:
        file_path = await _save_upload_file(file)
        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else 90,
            password=options.password if options else None,
            dpi=options.dpi if options else 200,
        )

        results = await conversion_service.pdf_to_images(file_path, service_options)

        return [_convert_service_result(r) for r in results]

    except Exception as e:
        return [ConversionResultPydantic(
            success=False,
            output_format="png",
            error=str(e),
        )]


@router.post("/conversion/images-to-pdf", response_model=ConversionResultPydantic)
async def images_to_pdf(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    options: Optional[ConversionOptionsPydantic] = None,
):
    """图片转PDF"""
    try:
        saved_files = []
        for file in files:
            file_path = await _save_upload_file(file)
            saved_files.append(file_path)

        service_options = ConversionOptions(
            preserve_formatting=options.preserve_formatting if options else True,
            quality=options.quality if options else None,
            page_size=options.page_size if options else None,
            orientation=options.orientation if options else None,
        )

        result = await conversion_service.images_to_pdf(saved_files, service_options)

        return _convert_service_result(result)

    except Exception as e:
        return ConversionResultPydantic(
            success=False,
            output_format="pdf",
            error=str(e),
        )


@router.post("/conversion/images-to-ppt", response_model=ConversionResultPydantic)
async def images_to_ppt(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    preserve_formatting: bool = Form(True),
    quality: Optional[int] = Form(None),
    ocr_mode: bool = Form(False),
):
    """图片转PPT"""
    try:
        logger.info(f"收到图片转PPT请求，文件数量: {len(files)}, OCR模式: {ocr_mode}")
        saved_files = []
        for file in files:
            logger.info(f"处理文件: {file.filename}, content_type: {file.content_type}")
            file_path = await _save_upload_file(file)
            saved_files.append(file_path)
            logger.info(f"文件已保存到: {file_path}")

        logger.info(f"所有文件已保存，开始转换，文件路径: {saved_files}")

        service_options = ConversionOptions(
            preserve_formatting=preserve_formatting,
            quality=quality,
            ocr_mode=ocr_mode,
        )

        result = await conversion_service.images_to_ppt(saved_files, service_options)
        logger.info(f"转换结果: {result}")

        return _convert_service_result(result)

    except Exception as e:
        logger.error(f"图片转PPT失败: {str(e)}", exc_info=True)
        return ConversionResultPydantic(
            success=False,
            output_format="pptx",
            error=str(e),
        )


@router.get("/conversion/document-info/{filename:path}")
async def get_document_info(filename: str):
    """获取文档信息（用于预览）"""
    try:
        file_path = Path(settings.upload_dir) / filename

        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        info = await conversion_service.get_document_info(file_path)

        return info

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion/outputs")
async def list_output_files():
    """列出生成的输出文件"""
    try:
        output_dir = Path(settings.output_dir)

        if not output_dir.exists():
            return {"files": []}

        files = []
        for file_path in output_dir.glob("*"):
            if file_path.is_file():
                files.append({
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "created_at": file_path.stat().st_ctime,
                })

        return {"files": files}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversion/download/{filename:path}")
async def download_output_file(filename: str):
    """下载转换后的文件"""
    try:
        output_dir = Path(settings.output_dir)
        file_path = output_dir / filename

        if not file_path.exists() or not file_path.is_file():
            raise HTTPException(status_code=404, detail="文件不存在")

        from fastapi.responses import FileResponse
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/octet-stream"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
