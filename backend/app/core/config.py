# Application Configuration
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置类"""

    app_name: str = "Document Processor"
    app_version: str = "0.1.0"
    debug: bool = False

    # API Settings
    api_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # File Storage
    upload_dir: str = "storage/uploads"
    output_dir: str = "storage/outputs"
    thumbnail_dir: str = "storage/thumbnails"
    max_file_size: int = 100 * 1024 * 1024  # 100MB

    # Supported Formats
    supported_formats: dict[str, list[str]] = {
        "pdf": [".pdf"],
        "word": [".doc", ".docx"],
        "excel": [".xls", ".xlsx"],
        "ppt": [".ppt", ".pptx"],
        "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"],
    }

    # Conversion Settings
    default_quality: int = 90
    default_compression: int = 3

    # Database
    db_url: str = "sqlite+aiosqlite:///storage/db/document_processor.db"

    # Search Index
    search_index_dir: str = "storage/db/search_index"
    index_dir: str = "storage/db/search_index"  # 别名，用于向后兼容

    # Annotations
    annotation_dir: str = "storage/annotations"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
