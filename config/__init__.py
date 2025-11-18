"""Configuration settings for the Vertex AI RAG engine."""

import os
from pathlib import Path


def _load_env_file() -> None:
    """Load key=value pairs from the workspace .env into os.environ."""

    base_env = Path(__file__).resolve().parents[2] / ".env"
    legacy_env = Path(__file__).resolve().parent / ".env"

    for env_path in (base_env, legacy_env):
        if not env_path.exists():
            continue
        for raw_line in env_path.read_text().splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            key, sep, value = line.partition("=")
            if not sep:
                continue
            if key not in os.environ:
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
GCS_DEFAULT_CONTENT_TYPE = _env("GCS_DEFAULT_CONTENT_TYPE", "application/pdf")

# RAG Corpus Settings
RAG_DEFAULT_EMBEDDING_MODEL = _env("RAG_DEFAULT_EMBEDDING_MODEL", "text-embedding-004")
RAG_DEFAULT_TOP_K = _env_int("RAG_DEFAULT_TOP_K", 10)
RAG_DEFAULT_SEARCH_TOP_K = _env_int("RAG_DEFAULT_SEARCH_TOP_K", 5)
RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD = _env_float(
    "RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD", 0.5
)
RAG_DEFAULT_PAGE_SIZE = _env_int("RAG_DEFAULT_PAGE_SIZE", 50)

# Agent Settings
AGENT_NAME = _env("RAG_AGENT_NAME", "rag_corpus_manager")
AGENT_MODEL = _env("RAG_AGENT_MODEL", "gemini-2.5-flash")
AGENT_OUTPUT_KEY = _env("RAG_AGENT_OUTPUT_KEY", "last_response")

# Logging Settings
LOG_LEVEL = _env("LOG_LEVEL", "INFO")
LOG_FORMAT = _env(
    "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
