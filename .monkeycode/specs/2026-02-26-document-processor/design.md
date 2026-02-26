# Document Processor

Feature Name: document-processor
Updated: 2026-02-26

## Description

文档处理工具是一个纯前端应用，支持PDF、Word、Excel、PPT、图片等常见格式的文档转换、检索、批注和页面管理，并提供文档拼接功能。采用本地部署方式，适用于个人和小团队场景，无需后端服务器支持。

## Architecture

### 系统架构图

```mermaid
graph TB
    subgraph "Presentation Layer"
        A1[文档列表视图]
        A2[文档预览视图]
        A3[转换向导视图]
        A4[检索面板]
        A5[批注面板]
        A6[页面管理面板]
        A7[文档拼接视图]
    end

    subgraph "Application Layer"
        B1[文档转换服务]
        B2[全文检索服务]
        B3[批注管理服务]
        B4[页面管理服务]
        B5[批量处理服务]
        B6[文档拼接服务]
    end

    subgraph "Domain Layer"
        C1[文档模型]
        C2[批注模型]
        C3[页面模型]
        C4[转换配置模型]
        C5[拼接配置模型]
    end

    subgraph "Infrastructure Layer"
        D1[PDF解析/生成器]
        D2[Office文档解析/生成器]
        D3[图片处理库]
        D4[索引引擎]
        D5[状态管理]
        D6[本地存储]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B2
    A5 --> B3
    A6 --> B4
    A7 --> B6

    B1 --> C1
    B1 --> C4
    B2 --> C1
    B3 --> C2
    B4 --> C3
    B5 --> C1
    B6 --> C5

    B1 --> D1
    B1 --> D2
    B1 --> D3
    B2 --> D4
    B3 --> D5
    B3 --> D6
    B4 --> D1
    B6 --> D1
```

### 技术栈选择

| 层级 | 技术选择 | 说明 |
|------|---------|------|
| 前端框架 | Vue 3 + TypeScript | 响应式UI，类型安全 |
| 构建工具 | Vite | 快速开发体验 |
| UI组件库 | Element Plus | 企业级组件支持 |
| 状态管理 | Pinia | 轻量级状态管理 |
| PDF处理 | pdf.js, pdf-lib | PDF解析和生成 |
| Office处理 | sheetjs, pptxgenjs | Excel/PPT处理 |
| Word处理 | mammoth | Word解析 |
| 图片处理 | html2canvas, sharp | 图片转换和处理 |
| 全文检索 | flexsearch | 高性能全文搜索 |
| 文件处理 | file-saver | 文件下载 |

### 目录结构

```
src/
├── assets/                 # 静态资源
├── components/             # Vue组件
│   ├── document/          # 文档相关组件
│   │   ├── DocumentList.vue
│   │   ├── DocumentPreview.vue
│   │   ├── PageThumbnail.vue
│   │   └── ConversionWizard.vue
│   ├── search/            # 搜索相关组件
│   │   ├── SearchPanel.vue
│   │   └── SearchResult.vue
│   ├── annotation/        # 批注相关组件
│   │   ├── AnnotationPanel.vue
│   │   ├── AnnotationMarker.vue
│   │   └── AnnotationList.vue
│   ├── page/              # 页面管理组件
│   │   ├── PageManager.vue
│   │   └── PageToolbar.vue
│   ├── merge/             # 文档拼接组件
│   │   ├── DocumentMergeView.vue
│   │   ├── PageSelector.vue
│   │   ├── MergeQueue.vue
│   │   └── PageRangeSelector.vue
│   └── common/            # 通用组件
│       ├── LoadingSpinner.vue
│       ├── ProgressBar.vue
│       └── ErrorAlert.vue
├── composables/           # 组合式函数
│   ├── useDocument.ts
│   ├── useSearch.ts
│   ├── useAnnotation.ts
│   ├── usePageManagement.ts
│   └── useDocumentMerge.ts
├── services/              # 服务层
│   ├── conversion.service.ts
│   ├── search.service.ts
│   ├── annotation.service.ts
│   ├── page.service.ts
│   ├── batch.service.ts
│   └── merge.service.ts
├── stores/                # 状态管理
│   ├── document.store.ts
│   ├── annotation.store.ts
│   ├── ui.store.ts
│   └── merge.store.ts
├── types/                 # 类型定义
│   ├── document.types.ts
│   ├── annotation.types.ts
│   ├── conversion.types.ts
│   └── merge.types.ts
├── utils/                 # 工具函数
│   ├── file.utils.ts
│   ├── format.utils.ts
│   └── validation.utils.ts
└── App.vue
```

## Components and Interfaces

### 文档转换服务 (ConversionService)

```typescript
interface ConversionOptions {
  preserveFormatting: boolean;    // 保持格式
  quality?: number;              // 输出质量
  password?: string;             // 文档密码
  includeAnnotations?: boolean;   // 包含批注
}

interface ConversionResult {
  success: boolean;
  outputBlob: Blob | null;
  outputFormat: string;
  warnings: string[];
  error?: string;
}

interface ConversionService {
  // PDF转Word
  pdfToWord(file: File, options: ConversionOptions): Promise<ConversionResult>;

  // Word转PDF
  wordToPdf(file: File, options: ConversionOptions): Promise<ConversionResult>;

  // PDF转Excel
  pdfToExcel(file: File, options: ConversionOptions): Promise<ConversionResult>;

  // Excel转PDF
  excelToPdf(file: File, options: ConversionOptions): Promise<ConversionResult>;

  // PDF转PPT
  pdfToPpt(file: File, options: ConversionOptions): Promise<ConversionResult>;

  // PPT转PDF
  pptToPdf(file: File, options: ConversionOptions): Promise<ConversionResult>;

  // 图片转PDF
  imageToPdf(files: File[], options: ConversionOptions): Promise<ConversionResult>;

  // PDF转图片
  pdfToImages(file: File, options: ConversionOptions): Promise<ConversionResult[]>;
}
```

### 全文检索服务 (SearchService)

```typescript
interface SearchOptions {
  caseSensitive: boolean;
  wholeWord: boolean;
  regex: boolean;
}

interface SearchResult {
  pageIndex: number;
  text: string;
  position: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

interface SearchService {
  // 建立索引
  buildIndex(documentId: string, content: string): void;

  // 执行搜索
  search(query: string, options: SearchOptions): SearchResult[];

  // 高亮显示
  highlight(results: SearchResult[]): void;

  // 导航到结果
  navigateTo(result: SearchResult): void;
}
```

### 批注管理服务 (AnnotationService)

```typescript
interface Annotation {
  id: string;
  documentId: string;
  pageIndex: number;
  position: Rectangle;
  content: string;
  author: string;
  createdAt: Date;
  updatedAt: Date;
  color: string;
}

interface Rectangle {
  x: number;
  y: number;
  width: number;
  height: number;
}

interface AnnotationService {
  // 添加批注
  add(annotation: Omit<Annotation, 'id' | 'createdAt' | 'updatedAt'>): Annotation;

  // 更新批注
  update(id: string, updates: Partial<Annotation>): void;

  // 删除批注
  remove(id: string): void;

  // 获取文档批注列表
  list(documentId: string): Annotation[];

  // 保存到本地存储
  saveToStorage(): void;

  // 从本地存储加载
  loadFromStorage(): void;
}
```

### 页面管理服务 (PageService)

```typescript
interface PageOperation {
  type: 'insert' | 'delete' | 'move' | 'rotate' | 'merge' | 'split';
  pageIndex: number;
  targetIndex?: number;
  rotation?: number;
}

interface PageService {
  // 插入页面
  insert(index: number, page: PDFPage): void;

  // 删除页面
  delete(index: number): void;

  // 移动页面
  move(fromIndex: number, toIndex: number): void;

  // 旋转页面
  rotate(index: number, degrees: 90 | 180 | 270): void;

  // 合并页面
  merge(indices: number[]): void;

  // 拆分页面
  split(index: number): void;

  // 获取页面缩略图
  getThumbnail(index: number): Promise<string>;
}
```

### 文档拼接服务 (MergeService)

```typescript
interface SelectedPage {
  id: string;
  documentId: string;
  pageIndex: number;
  originalDocumentName: string;
  thumbnail: string;
  pageWidth: number;
  pageHeight: number;
  rotation: number;
}

interface MergeConfig {
  pageSize?: 'A4' | 'A3' | 'Letter' | 'auto';
  orientation?: 'portrait' | 'landscape' | 'keep-original';
  outputFileName: string;
  includeBookmarks?: boolean;
  metadata?: {
    title?: string;
    author?: string;
    subject?: string;
  };
}

interface MergeResult {
  success: boolean;
  outputBlob: Blob | null;
  totalPages: number;
  warnings: string[];
  error?: string;
}

interface MergeService {
  // 选择页面
  selectPage(selectedPage: SelectedPage): void;

  // 取消选择页面
  deselectPage(pageId: string): void;

  // 批量选择页面范围
  selectPageRange(documentId: string, startIndex: number, endIndex: number): void;

  // 全选/取消全选文档的所有页面
  toggleAllPages(documentId: string): void;

  // 调整拼接队列中页面顺序
  reorderPage(pageId: string, newIndex: number): void;

  // 清空拼接队列
  clearQueue(): void;

  // 获取当前拼接队列
  getQueue(): SelectedPage[];

  // 生成合并后的PDF
  mergeDocuments(config: MergeConfig): Promise<MergeResult>;

  // 预览合并结果
  previewMerge(): Promise<string[]>;
}
```

## Data Models

### 文档模型

```typescript
interface Document {
  id: string;
  name: string;
  type: DocumentType;
  size: number;
  createdAt: Date;
  modifiedAt: Date;
  pageCount: number;
  previewUrl?: string;
  metadata: DocumentMetadata;
}

enum DocumentType {
  PDF = 'pdf',
  WORD = 'word',
  EXCEL = 'excel',
  PPT = 'ppt',
  IMAGE = 'image'
}

interface DocumentMetadata {
  title?: string;
  author?: string;
  subject?: string;
  keywords?: string;
  creator?: string;
  producer?: string;
  creationDate?: Date;
  modificationDate?: Date;
}
```

### 转换配置模型

```typescript
interface ConversionConfig {
  sourceFormat: DocumentType;
  targetFormat: DocumentType;
  preserveFormatting: boolean;
  outputQuality: number;        // 1-100
  compressionLevel: number;      // 0-9
  includeAnnotations: boolean;
  password?: string;
}
```

### 批注模型

```typescript
interface Annotation {
  id: string;                    // UUID
  documentId: string;
  pageIndex: number;
  position: Rectangle;
  content: string;
  author: string;
  color: string;
  createdAt: Date;
  updatedAt: Date;
}
```

### 页面模型

```typescript
interface Page {
  index: number;
  width: number;
  height: number;
  rotation: number;              // 0, 90, 180, 270
  thumbnail: string;
  content?: PageContent;
}

interface PageContent {
  text?: string;                 // 用于检索的文本内容
  elements?: PageElement[];
}

interface PageElement {
  type: 'text' | 'image' | 'table' | 'shape';
  position: Rectangle;
  content: any;
  style?: any;
}
```

### 拼接配置模型

```typescript
interface MergeConfig {
  pageSize: 'A4' | 'A3' | 'Letter' | 'auto';
  orientation: 'portrait' | 'landscape' | 'keep-original';
  outputFileName: string;
  includeBookmarks: boolean;
  metadata?: {
    title?: string;
    author?: string;
    subject?: string;
  };
}

interface SelectedPage {
  id: string;
  documentId: string;
  pageIndex: number;
  originalDocumentName: string;
  thumbnail: string;
  pageWidth: number;
  pageHeight: number;
  rotation: number;
}

interface MergeQueue {
  pages: SelectedPage[];
  totalCount: number;
  documents: Set<string>;
}
```

## Correctness Properties

### 文档转换正确性

1. **格式兼容性**: 对于每种支持的源格式和目标格式组合，转换后的文档必须能够被对应的阅读器正确打开和显示
2. **文本完整性**: 转换过程中不得丢失原文档中的任何文本内容
3. **结构保持性**: 文档的基本层级结构（章节、段落等）在转换后必须保持
4. **嵌入对象保留**: 原文档中的嵌入对象（图片、表格、公式等）在转换后必须存在

### 排版保真度正确性

1. **字体样式一致性**: 转换后的字体样式（名称、大小、颜色、粗细、斜体）与原文档的差异不超过5%
2. **位置精度**: 文本块和图像元素的位置偏移不超过原始尺寸的2%
3. **表格结构保持**: 表格的行列结构、合并单元格配置在转换后完全一致

### 检索正确性

1. **结果完整性**: 检索结果必须包含文档中所有匹配的文本片段
2. **无遗漏**: 不得遗漏任何匹配的位置
3. **无误报**: 不应返回不匹配文本的结果
4. **位置准确性**: 返回的匹配位置坐标误差不超过5像素

### 批注正确性

1. **关联一致性**: 批注必须与其关联的文本或区域正确绑定
2. **数据完整性**: 批注的创建时间、修改时间、作者等信息不得丢失或篡改
3. **持久性**: 存储的批注数据在应用重启后能够正确恢复

### 页面操作正确性

1. **索引一致性**: 页面操作后的页面索引必须连续且唯一
2. **内容完整性**: 页面移动、旋转操作不得改变页面内容
3. **合并逻辑**: 合并多个页面时，所有源页面的内容必须出现在结果页面中

### 文档拼接正确性

1. **页面顺序保持性**: 拼接结果中的页面顺序必须与用户在拼接队列中定义的顺序完全一致
2. **内容完整性**: 所有选中的页面内容必须完整出现在结果文档中，不得有遗漏或重复
3. **跨文档正确性**: 来自不同文档的页面能够正确合并到同一文档中
4. **页面尺寸处理**: 根据配置正确处理不同尺寸的页面（统一尺寸或保持原尺寸）
5. **方向一致性**: 根据配置正确处理不同方向的页面
6. **元数据准确性**: 生成的PDF元数据必须与用户配置一致

## Error Handling

### 文件处理错误

| 错误类型 | 处理策略 |
|---------|---------|
| 文件格式不支持 | 显示支持的格式列表，提示用户重新选择 |
| 文件损坏或无法解析 | 显示"文件无法解析"错误，提供重试选项 |
| 文件大小超过限制 | 显示当前限制和文件大小，提示用户压缩后重试 |
| 密码保护文档 | 弹出密码输入框，验证失败后提示错误 |
| 内存不足 | 显示"内存不足"提示，建议关闭其他文档或分批处理 |

### 转换错误

| 错误类型 | 处理策略 |
|---------|---------|
| 转换失败 | 显示具体错误信息，提供查看详情选项 |
| 部分内容转换失败 | 记录警告信息，标记问题区域，继续转换 |
| 超时 | 显示"转换超时"提示，建议简化文档或分批处理 |
| 格式特性不支持 | 列出不支持的特性，提供替代方案 |

### 检索错误

| 错误类型 | 处理策略 |
|---------|---------|
| 正则表达式语法错误 | 显示"正则表达式语法错误"，提供修正建议 |
| 搜索超时 | 显示"搜索超时"，建议缩小搜索范围 |
| 无结果 | 显示"未找到匹配结果"友好提示 |

### 批注错误

| 错误类型 | 处理策略 |
|---------|---------|
| 批注保存失败 | 显示"保存失败"，提供重试选项 |
| 批注数据损坏 | 检测到数据损坏时清除损坏数据，恢复可读部分 |
| 存储空间不足 | 显示"存储空间不足"，提示用户清理旧数据 |

### 页面管理错误

| 错误类型 | 处理策略 |
|---------|---------|
| 页面索引越界 | 禁止越界操作，显示有效范围提示 |
| 页面合并冲突 | 检测到冲突时提示用户选择操作方式 |
| 缩略图生成失败 | 显示默认图标，记录错误日志 |

### 文档拼接错误

| 错误类型 | 处理策略 |
|---------|---------|
| 拼接队列为空 | 禁用生成按钮，提示用户选择页面 |
| 页面加载失败 | 标记失败页面，继续处理其他页面，生成警告报告 |
| 文档格式不兼容 | 自动转换非PDF文档为PDF后继续，或提示用户手动转换 |
| 内存不足 | 显示"内存不足"提示，建议减少拼接页面数量或分批处理 |
| 生成失败 | 显示具体错误信息，提供重试选项 |
| 页面尺寸差异 | 显示警告信息，说明将使用统一尺寸处理 |

## Test Strategy

### 单元测试

1. **文档解析测试**: 验证各格式文档能够正确解析，提取文本和结构信息
2. **转换逻辑测试**: 验证各格式转换的结果符合预期
3. **检索算法测试**: 验证检索结果的准确性和完整性
4. **批注操作测试**: 验证批注的增删改查功能正确性
5. **页面操作测试**: 验证页面插入、删除、移动、旋转等操作的正确性
6. **文档拼接测试**: 验证页面选择、排序、合并功能的正确性

### 集成测试

1. **端到端转换测试**: 完整测试从文件上传到转换结果导出的全流程
2. **批量处理测试**: 验证批量转换的并发处理和错误隔离
3. **存储持久化测试**: 验证应用状态在刷新后的恢复能力
4. **跨文档拼接测试**: 验证从多个文档选择页面并合并的完整流程

### 兼容性测试

1. **浏览器兼容性**: 测试Chrome、Firefox、Edge、Safari各版本
2. **文档格式兼容性**: 测试不同版本生成的文档文件
3. **操作系统兼容性**: 测试Windows、macOS、Linux平台

### 性能测试

1. **大文件处理**: 测试100MB文件的加载和转换性能
2. **多文档并发**: 测试同时处理10个文档的性能表现
3. **检索性能**: 测试在100页文档中检索的响应时间
4. **内存占用**: 监控长时间使用后的内存使用情况

### 排版保真度测试

1. **自动化对比**: 使用图像对比工具计算转换前后页面的相似度
2. **人工验证**: 对转换结果进行人工抽样检查，确保排版质量

### 回归测试

每次更新后运行完整测试套件，确保新功能不影响现有功能。

## Implementation Plan

### 阶段一：基础框架搭建

1. 项目初始化（Vue 3 + Vite + TypeScript）
2. 基础UI组件集成（Element Plus）
3. 状态管理配置（Pinia）
4. 路由配置
5. 文件上传组件开发

### 阶段二：文档处理核心

1. PDF解析和渲染（pdf.js）
2. PDF生成（pdf-lib）
3. Office文档解析（sheetjs, mammoth, pptxgenjs）
4. 图片处理集成（html2canvas）
5. 文档模型定义

### 阶段三：格式转换实现

1. PDF与Word互转
2. PDF与Excel互转
3. PDF与PPT互转
4. 图片与PDF互转
5. 转换向导UI开发

### 阶段四：全文检索功能

1. 索引引擎集成（flexsearch）
2. 搜索界面开发
3. 结果高亮显示
4. 正则表达式支持

### 阶段五：批注编辑功能

1. 批注数据模型
2. 批注标记UI
3. 批注面板开发
4. 本地存储持久化

### 阶段六：页面管理功能

1. 页面缩略图生成
2. 页面操作工具栏
3. 拖拽排序功能
4. 页面旋转、删除等操作

### 阶段七：文档拼接功能

1. 文档拼接视图开发
2. 页面选择器组件
3. 拼接队列组件
4. 页面范围选择器
5. 拖拽排序功能
6. 文档合并逻辑实现

### 阶段八：批量处理

1. 批量转换逻辑
2. 进度显示
3. 结果报告

### 阶段九：优化与完善

1. 性能优化
2. 错误处理完善
3. 用户体验优化
4. 文档编写

## References

[^1]: (Website) - [pdf.js Documentation](https://mozilla.github.io/pdf.js/)
[^2]: (Website) - [pdf-lib Documentation](https://pdf-lib.js.org/)
[^3]: (Website) - [SheetJS Documentation](https://docs.sheetjs.com/)
[^4]: (Website) - [FlexSearch Documentation](https://github.com/nextapps-de/flexsearch)
[^5]: (Website) - [Vue 3 Documentation](https://vuejs.org/)
