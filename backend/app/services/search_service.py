# Search Service
from typing import List, Optional, Dict, Any
from pathlib import Path
import json
import re

try:
    from whoosh.index import create_in, exists_in, open_dir
    from whoosh.fields import Schema, TEXT, ID, STORED
    from whoosh.qparser import QueryParser, OrGroup, AndGroup
    from whoosh.analysis import StandardAnalyzer
    WHOOSH_AVAILABLE = True
except ImportError:
    WHOOSH_AVAILABLE = False

from PyPDF2 import PdfReader


class SearchOptions:
    def __init__(
        self,
        case_sensitive: bool = False,
        whole_word: bool = False,
        regex: bool = False,
        page_limit: int = 20,
    ):
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        self.regex = regex
        self.page_limit = page_limit


class SearchResult:
    def __init__(
        self,
        page_index: int,
        text: str,
        position: dict,
        highlights: List[str] = None,
    ):
        self.page_index = page_index
        self.text = text
        self.position = position
        self.highlights = highlights or []


class SearchService:
    """全文检索服务"""

    def __init__(self, index_dir: str):
        """初始化搜索服务"""
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.schema = Schema(
            document_id=ID(stored=True, unique=True),
            page_number=STORED(),
            content=TEXT(analyzer=StandardAnalyzer()),
            text_stored=STORED(),
        )

        if WHOOSH_AVAILABLE:
            if not exists_in(str(self.index_dir)):
                self.ix = create_in(str(self.index_dir), schema=self.schema)
            else:
                self.ix = open_dir(str(self.index_dir))
        else:
            self.ix = None
            # 简单的内存存储作为后备方案
            self._memory_index: Dict[str, List[Dict]] = {}

    def build_index(self, document_id: str, pdf_path: str) -> Dict[str, Any]:
        """为PDF文档建立索引

        Args:
            document_id: 文档ID
            pdf_path: PDF文件路径

        Returns:
            包含索引状态和统计信息的字典
        """
        try:
            pdf_file = Path(pdf_path)
            if not pdf_file.exists():
                return {"success": False, "error": "文件不存在"}

            reader = PdfReader(str(pdf_path))
            total_pages = len(reader.pages)
            indexed_pages = 0

            if WHOOSH_AVAILABLE:
                writer = self.ix.writer()

                for page_num, page in enumerate(reader.pages):
                    try:
                        # 提取页面文本
                        text = page.extract_text() or ""

                        # 限制文本长度
                        if len(text) > 10000:
                            text = text[:10000]

                        if text.strip():
                            writer.add_document(
                                document_id=document_id,
                                page_number=page_num + 1,
                                content=text,
                                text_stored=text,
                            )
                            indexed_pages += 1
                    except Exception as e:
                        print(f"索引页面 {page_num + 1} 失败: {e}")
                        continue

                writer.commit()
            else:
                # 后备方案：使用简单内存索引
                self._memory_index[document_id] = []
                for page_num, page in enumerate(reader.pages):
                    try:
                        text = page.extract_text() or ""
                        if text.strip():
                            self._memory_index[document_id].append({
                                "page_number": page_num + 1,
                                "content": text,
                            })
                            indexed_pages += 1
                    except Exception as e:
                        print(f"索引页面 {page_num + 1} 失败: {e}")
                        continue

            return {
                "success": True,
                "total_pages": total_pages,
                "indexed_pages": indexed_pages,
                "document_id": document_id,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    def search(
        self, document_id: str, query: str, options: SearchOptions
    ) -> List[SearchResult]:
        """执行搜索

        Args:
            document_id: 文档ID
            query: 搜索查询
            options: 搜索选项

        Returns:
            搜索结果列表
        """
        if WHOOSH_AVAILABLE:
            return self._search_whoosh(document_id, query, options)
        else:
            return self._search_simple(document_id, query, options)

    def _search_whoosh(
        self, document_id: str, query: str, options: SearchOptions
    ) -> List[SearchResult]:
        """使用Whoosh进行搜索"""
        results = []

        try:
            with self.ix.searcher() as searcher:
                # 构建查询
                if options.regex:
                    # 正则表达式查询
                    parser = QueryParser("content", self.ix.schema)
                    q = parser.parse(query)
                elif options.whole_word:
                    # 全词匹配
                    parser = QueryParser("content", self.ix.schema)
                    terms = query.strip().split()
                    if len(terms) == 1:
                        q = parser.parse(f'"{query}"')
                    else:
                        q = parser.parse(" AND ".join([f'"{t}"' for t in terms]))
                else:
                    # 默认：OR查询，匹配任意词
                    parser = QueryParser(
                        "content", self.ix.schema, group=OrGroup
                    )
                    q = parser.parse(query)

                # 执行搜索
                hits = searcher.search(q, limit=options.page_limit * 10)

                # 过滤特定文档的结果
                for hit in hits:
                    if hit["document_id"] == document_id:
                        text = hit.get("text_stored", "")
                        highlights = self._extract_highlights(text, query, options)

                        results.append(
                            SearchResult(
                                page_index=hit["page_number"] - 1,
                                text=text[:500] + "..." if len(text) > 500 else text,
                                position={"page": hit["page_number"]},
                                highlights=highlights,
                            )
                        )

                        if len(results) >= options.page_limit:
                            break

        except Exception as e:
            print(f"Whoosh搜索失败: {e}")

        return results

    def _search_simple(
        self, document_id: str, query: str, options: SearchOptions
    ) -> List[SearchResult]:
        """简单搜索（无Whoosh时的后备方案）"""
        results = []

        if document_id not in self._memory_index:
            return results

        pages = self._memory_index[document_id]

        # 准备查询模式
        if options.regex:
            pattern = re.compile(query)
        elif options.whole_word:
            pattern = re.compile(rf"\b{re.escape(query)}\b")
        else:
            if options.case_sensitive:
                pattern = re.compile(re.escape(query))
            else:
                pattern = re.compile(re.escape(query), re.IGNORECASE)

        for page_data in pages:
            content = page_data["content"]
            matches = list(pattern.finditer(content))

            if matches:
                highlights = self._extract_highlights(content, query, options)
                results.append(
                    SearchResult(
                        page_index=page_data["page_number"] - 1,
                        text=content[:500] + "..." if len(content) > 500 else content,
                        position={"page": page_data["page_number"]},
                        highlights=highlights,
                    )
                )

                if len(results) >= options.page_limit:
                    break

        return results

    def _extract_highlights(
        self, text: str, query: str, options: SearchOptions
    ) -> List[str]:
        """提取高亮片段"""
        highlights = []
        context_size = 30

        # 准备搜索模式
        if options.regex:
            pattern = re.compile(query)
        elif options.whole_word:
            pattern = re.compile(rf"\b{re.escape(query)}\b")
        else:
            if options.case_sensitive:
                pattern = re.compile(re.escape(query))
            else:
                pattern = re.compile(re.escape(query), re.IGNORECASE)

        for match in pattern.finditer(text):
            start = max(0, match.start() - context_size)
            end = min(len(text), match.end() + context_size)
            highlight = text[start:end]
            highlights.append(highlight)

            if len(highlights) >= 3:
                break

        return highlights

    def highlight_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """高亮显示结果中的匹配文本"""
        return results

    def delete_index(self, document_id: str) -> bool:
        """删除文档的索引"""
        try:
            if WHOOSH_AVAILABLE:
                writer = self.ix.writer()
                writer.delete_by_term("document_id", document_id)
                writer.commit()
            else:
                if document_id in self._memory_index:
                    del self._memory_index[document_id]
            return True
        except Exception as e:
            print(f"删除索引失败: {e}")
            return False

    def get_index_info(self, document_id: str) -> Dict[str, Any]:
        """获取索引信息"""
        try:
            if WHOOSH_AVAILABLE:
                with self.ix.searcher() as searcher:
                    # 查询文档是否存在
                    q = QueryParser("document_id", self.ix.schema).parse(document_id)
                    hits = searcher.search(q, limit=1)
                    if hits:
                        return {
                            "indexed": True,
                            "page_count": len(list(searcher.search(q))),
                        }
            else:
                if document_id in self._memory_index:
                    return {
                        "indexed": True,
                        "page_count": len(self._memory_index[document_id]),
                    }

            return {"indexed": False, "page_count": 0}

        except Exception as e:
            return {"indexed": False, "page_count": 0, "error": str(e)}
