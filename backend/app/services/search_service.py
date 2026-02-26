# Search Service
from typing import List, Optional
from pathlib import Path


class SearchOptions:
    def __init__(
        self,
        case_sensitive: bool = False,
        whole_word: bool = False,
        regex: bool = False,
    ):
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        self.regex = regex


class SearchResult:
    def __init__(
        self,
        page_index: int,
        text: str,
        position: dict,
    ):
        self.page_index = page_index
        self.text = text
        self.position = position


class SearchService:
    """全文检索服务"""

    def __init__(self, index_dir: str):
        """初始化搜索服务"""
        self.index_dir = index_dir
        # TODO: Initialize Whoosh index

    def build_index(self, document_id: str, content: str) -> None:
        """建立索引"""
        # TODO: Implement index building with Whoosh
        pass

    def search(
        self, query: str, options: SearchOptions
    ) -> List[SearchResult]:
        """执行搜索"""
        # TODO: Implement search with Whoosh
        return []

    def highlight_results(self, results: List[SearchResult]) -> None:
        """高亮显示结果"""
        # TODO: Implement highlighting
        pass
