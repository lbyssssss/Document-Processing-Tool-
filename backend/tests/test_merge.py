# Merge Service Tests
import pytest
from app.services.merge_service import MergeService, MergeConfig, SelectedPage


@pytest.fixture
def merge_service():
    """拼接服务fixture"""
    return MergeService()


@pytest.fixture
def sample_page():
    """示例页面fixture"""
    return SelectedPage(
        id="page_1",
        document_id="doc_1",
        page_index=0,
        original_document_name="test.pdf",
        thumbnail="/thumb/page1.jpg",
        page_width=595.28,
        page_height=841.89,
        rotation=0,
    )


def test_merge_service_init(merge_service):
    """测试拼接服务初始化"""
    assert merge_service is not None
    assert len(merge_service.get_queue()) == 0


def test_merge_config_defaults(merge_service):
    """测试拼接配置默认值"""
    config = MergeConfig()
    assert config.page_size == "auto"
    assert config.orientation == "keep-original"
    assert config.include_bookmarks is False
    assert config.metadata is None


def test_get_queue_empty(merge_service):
    """测试获取空队列"""
    queue = merge_service.get_queue()
    assert isinstance(queue, list)
    assert len(queue) == 0


# TODO: Add actual merge tests when implemented
