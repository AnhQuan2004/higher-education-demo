"""Configuration settings for the Vertex AI RAG engine (legacy module)."""

import os
from pathlib import Path


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    root_env = Path(__file__).resolve().parent.parent / ".env"
    for candidate in (root_env, env_path):
        if not candidate.exists():
            continue
        for raw_line in candidate.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if sep and key not in os.environ:
                os.environ[key.strip()] = value.strip()


_load_env_file()


def _env(key: str, default: str | None = None) -> str | None:
    return os.environ.get(key, default)


def _env_int(key: str, default: int) -> int:
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


# Google Cloud Project Settings
PROJECT_ID = _env("GOOGLE_CLOUD_PROJECT", _env("VERTEXAI_PROJECT"))
LOCATION = _env("GOOGLE_CLOUD_LOCATION", _env("VERTEXAI_LOCATION", "asia-east1"))

# GCS Storage Settings
GCS_DEFAULT_STORAGE_CLASS = _env("GCS_DEFAULT_STORAGE_CLASS", "STANDARD")
GCS_DEFAULT_LOCATION = _env("GCS_DEFAULT_LOCATION", "US")
GCS_LIST_BUCKETS_MAX_RESULTS = _env_int("GCS_LIST_BUCKETS_MAX_RESULTS", 50)
GCS_LIST_BLOBS_MAX_RESULTS = _env_int("GCS_LIST_BLOBS_MAX_RESULTS", 100)

# RAG Corpus Settings
RAG_DEFAULT_EMBEDDING_MODEL = _env("RAG_DEFAULT_EMBEDDING_MODEL", "text-embedding-004")
RAG_DEFAULT_TOP_K = _env_int("RAG_DEFAULT_TOP_K", 10)
RAG_DEFAULT_SEARCH_TOP_K = _env_int("RAG_DEFAULT_SEARCH_TOP_K", 5)
RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD = _env_float(
    "RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD", 0.5
)
RAG_DEFAULT_PAGE_SIZE = _env_int("RAG_DEFAULT_PAGE_SIZE", 50)

# Parallel Search Settings
MAX_SEARCH_WORKERS = _env_int("MAX_SEARCH_WORKERS", 4)
CORPUS_SEARCH_TIMEOUT = _env_float("CORPUS_SEARCH_TIMEOUT", 10.0)

# Logging Settings
LOG_LEVEL = _env("LOG_LEVEL", "INFO")
