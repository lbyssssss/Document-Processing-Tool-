# Document Processor Backend

文档处理工具的后端服务，使用FastAPI构建。

## 技术栈

- FastAPI - Web框架
- PyPDF2 - PDF处理
- pdfplumber - PDF解析
- reportlab - PDF生成
- python-docx - Word处理
- openpyxl - Excel处理
- python-pptx - PPT处理
- Pillow - 图片处理
- Whoosh - 全文检索

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行服务

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 运行测试

```bash
pytest
```

## API文档

启动服务后访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
