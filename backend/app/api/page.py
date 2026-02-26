# Page Management API
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/page", tags=["page"])


class Page(BaseModel):
    id: str
    number: int
    width: float = 595.28  # A4 宽度
    height: float = 841.89  # A4 高度
    rotation: float = 0.0
    thumbnail: Optional[str] = None


class PageList(BaseModel):
    document_id: str
    total_pages: int
    pages: List[Page]


class PageOperation(BaseModel):
    action: str  # rotate, move, delete
    params: Optional[dict] = None


class PageResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


class PageThumbnailResponse(BaseModel):
    success: bool
    page_number: int
    thumbnail_path: Optional[str] = None


# 存储页面信息的文件路径
_PAGE_INFO_FILE = Path(settings.output_dir) / "pages_info.json"


def _load_page_info():
    """加载页面信息"""
    if _PAGE_INFO_FILE.exists():
        with open(_PAGE_INFO_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_page_info(info: dict):
    """保存页面信息"""
    with open(_PAGE_INFO_FILE, "w", encoding="utf-8") as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


def _extract_pdf_pages(file_path: Path) -> List[dict]:
    """从 PDF 提取页面信息"""
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(file_path))
        pages = []
        for i, page in enumerate(reader.pages):
            pages.append({
                "number": i + 1,
                "width": float(page.mediabox.width),
                "height": float(page.mediabox.height),
                "rotation": float(page.rotation) if page.rotation else 0.0,
            })
        return pages
    except Exception as e:
        logger.error(f"提取 PDF 页面信息失败: {e}")
        return []


@router.post("/upload", response_model=dict)
async def upload_document(file: UploadFile = File(...)):
    """上传文档并提取页面信息"""
    try:
        import uuid
        from pathlib import Path

        file_id = str(uuid.uuid4())
        file_ext = Path(file.filename).suffix
        upload_path = Path(settings.upload_dir) / f"{file_id}{file_ext}"

        # 保存文件
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        with open(upload_path, "wb") as f:
            from shutil import copyfileobj
            copyfileobj(file.file, f)

        # 提取页面信息
        if file_ext.lower() == ".pdf":
            pages_info = _extract_pdf_pages(upload_path)
        else:
            # 非PDF文件，创建默认页面
            pages_info = [{"number": 1, "width": 595.28, "height": 841.89, "rotation": 0.0}]

        # 保存页面信息
        all_page_info = _load_page_info()
        all_page_info[file_id] = {
            "filename": file.filename,
            "file_path": str(upload_path),
            "pages": pages_info,
        }
        _save_page_info(all_page_info)

        logger.info(f"文档上传成功: {file_id}, 共 {len(pages_info)} 页")

        return {
            "success": True,
            "document_id": file_id,
            "filename": file.filename,
            "total_pages": len(pages_info),
            "pages": [
                {"id": f"{file_id}_page_{p['number']}", **p}
                for p in pages_info
            ],
        }

    except Exception as e:
        logger.error(f"上传文档失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/pages", response_model=PageList)
async def get_pages(document_id: str):
    """获取文档的所有页面"""
    try:
        all_page_info = _load_page_info()
        doc_info = all_page_info.get(document_id)

        if not doc_info:
            raise HTTPException(status_code=404, detail="文档不存在")

        pages = [
            Page(
                id=f"{document_id}_page_{p['number']}",
                number=p['number'],
                width=p.get('width', 595.28),
                height=p.get('height', 841.89),
                rotation=p.get('rotation', 0.0),
            )
            for p in doc_info.get('pages', [])
        ]

        return PageList(
            document_id=document_id,
            total_pages=len(pages),
            pages=pages,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取页面信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/pages/{page_id}", response_model=PageResponse)
async def update_page(document_id: str, page_id: str, operation: PageOperation):
    """更新页面（旋转、移动、删除）"""
    try:
        all_page_info = _load_page_info()
        doc_info = all_page_info.get(document_id)

        if not doc_info:
            raise HTTPException(status_code=404, detail="文档不存在")

        action = operation.action
        params = operation.params or {}

        if action == "rotate":
            # 旋转页面
            angle = params.get("angle", 90)
            page_num = int(page_id.split("_")[-1])
            for p in doc_info["pages"]:
                if p["number"] == page_num:
                    current_rotation = p.get("rotation", 0)
                    p["rotation"] = (current_rotation + angle) % 360
                    break

        elif action == "move":
            # 移动页面（重新排序）
            from_index = params.get("from_index")
            to_index = params.get("to_index")
            if from_index is not None and to_index is not None:
                pages = doc_info["pages"]
                if 0 <= from_index < len(pages) and 0 <= to_index < len(pages):
                    page = pages.pop(from_index)
                    pages.insert(to_index, page)
                    # 更新页面编号
                    for i, p in enumerate(pages):
                        p["number"] = i + 1

        elif action == "delete":
            # 删除页面
            page_num = int(page_id.split("_")[-1])
            doc_info["pages"] = [
                p for p in doc_info["pages"] if p["number"] != page_num
            ]
            # 更新页面编号
            for i, p in enumerate(doc_info["pages"]):
                p["number"] = i + 1

        _save_page_info(all_page_info)

        logger.info(f"页面操作成功: {document_id}/{page_id}, 动作: {action}")

        return PageResponse(
            success=True,
            message=f"{action} 操作成功",
            data={"action": action, "page_id": page_id},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"页面操作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/pages", response_model=PageResponse)
async def add_page(document_id: str, page: Page):
    """添加新页面（从其他文档）"""
    try:
        all_page_info = _load_page_info()

        if document_id not in all_page_info:
            all_page_info[document_id] = {
                "filename": f"merged_{document_id}",
                "file_path": "",
                "pages": [],
            }

        # 添加新页面
        new_page_info = {
            "number": len(all_page_info[document_id]["pages"]) + 1,
            "width": page.width,
            "height": page.height,
            "rotation": page.rotation,
        }
        all_page_info[document_id]["pages"].append(new_page_info)

        _save_page_info(all_page_info)

        logger.info(f"添加页面成功: {document_id}, 页码: {new_page_info['number']}")

        return PageResponse(
            success=True,
            message="页面添加成功",
            data={"page_number": new_page_info["number"]},
        )

    except Exception as e:
        logger.error(f"添加页面失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/page/{page_number}/thumbnail", response_model=PageThumbnailResponse)
async def get_page_thumbnail(document_id: str, page_number: int):
    """获取页面缩略图"""
    try:
        all_page_info = _load_page_info()
        doc_info = all_page_info.get(document_id)

        if not doc_info:
            raise HTTPException(status_code=404, detail="文档不存在")

        file_path = Path(doc_info.get("file_path", ""))
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")

        # 生成缩略图
        thumbnail_dir = Path(settings.thumbnail_dir)
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        thumbnail_path = thumbnail_dir / f"{document_id}_page_{page_number}.png"

        if not thumbnail_path.exists():
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(str(file_path), first_page=page_number, last_page=page_number, dpi=72)
                if images:
                    images[0].save(str(thumbnail_path), "PNG")
            except ImportError:
                # 如果 pdf2image 不可用，返回空
                pass

        return PageThumbnailResponse(
            success=True,
            page_number=page_number,
            thumbnail_path=str(thumbnail_path) if thumbnail_path.exists() else None,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取缩略图失败: {e}")
        return PageThumbnailResponse(
            success=False,
            page_number=page_number,
        )
