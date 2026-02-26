# Test Configuration
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def test_settings():
    """测试配置"""
    from app.core.config import Settings
    return Settings(debug=True)
