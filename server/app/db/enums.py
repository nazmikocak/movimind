"""Veritabanı enum tiplerinin Python karşılıkları (database/V1__init.sql)."""
from enum import StrEnum


class MetaKey(StrEnum):
    """`app_meta_key` enum'u: `app_meta` tablosunun izinli anahtarları."""

    ANALYSIS = "analysis"
    DATASET_STATS = "dataset_stats"
    MODEL_INFO = "model_info"
    MODEL_VERSION = "model_version"
    PUBLISHED_AT = "published_at"
