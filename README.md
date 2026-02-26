# Document Processor

一个基于Python和Vue的文档处理工具，支持PDF、Word、Excel、PPT、图片等常见格式的文档转换、检索、批注和页面管理，并提供文档拼接功能。

## 技术栈

### 后端
- FastAPI - Web框架
- PyPDF2 - PDF处理
- pdfplumber - PDF解析
- reportlab - PDF生成
- python-docx - Word处理
- openpyxl - Excel处理
- python-pptx - PPT处理
- Pillow - 图片处理
- Whoosh - 全文检索
- SQLite - 数据存储

### 前端
- Vue 3 - 前端框架
- TypeScript - 类型安全
- Vite - 构建工具
- Element Plus - UI组件库
- Pinia - 状态管理

## 项目结构

```
document-processor/
├── backend/               # Python后端
│   ├── app/
│   │   ├── api/        # API路由
│   │   ├── core/       # 核心配置
│   │   ├── models/     # 数据模型
│   │   ├── services/   # 业务逻辑服务
│   │   └── utils/      # 工具函数
│   ├── storage/        # 文件存储
│   ├── tests/          # 测试
│   └── requirements.txt
├── frontend/          # Vue前端
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   ├── stores/
│   │   ├── services/
│   │   └── types/
│   └── package.json
└── README.md
```

## 功能特性

- 文档格式转换（PDF、Word、Excel、PPT、图片）
- 全文检索
- 批注编辑
- 页面管理
- 文档拼接

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 许可证

MIT
