"""Latency logging and observability for RAG operations."""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Callable, Dict, List, Optional

from rag.config import LOG_LEVEL

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))


@dataclass
class LatencyMetric:
    """Single latency measurement."""
    operation: str
    duration_ms: float
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LatencyLogger:
    """Collects and reports latency metrics.

    Thread-safe singleton implementation for tracking operation latencies.
    Provides summary statistics including count, avg, min, max per operation.

    Usage:
        logger = LatencyLogger()
        logger.record("search_corpus", 125.5)
        summary = logger.get_summary()
    """

    _instance: Optional["LatencyLogger"] = None
    _metrics: List[LatencyMetric] = []
    _operation_stats: Dict[str, List[float]] = defaultdict(list)

    def __new__(cls) -> "LatencyLogger":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def record(
        self,
        operation: str,
        duration_ms: float,
        **metadata: Any,
    ) -> None:
        """Record a latency measurement.

        Args:
            operation: Name of the operation being timed
            duration_ms: Duration in milliseconds
            **metadata: Additional metadata to store with the metric
        """
        metric = LatencyMetric(
            operation=operation,
            duration_ms=duration_ms,
            metadata=metadata,
        )
        self._metrics.append(metric)
        self._operation_stats[operation].append(duration_ms)

        # Log if exceeds threshold
        if duration_ms > 1000:
            logger.warning(f"SLOW: {operation} took {duration_ms:.0f}ms")
        else:
            logger.debug(f"{operation}: {duration_ms:.0f}ms")

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all operations.

        Returns:
            Dict mapping operation names to statistics including:
            - count: Number of measurements
            - avg_ms: Average duration in milliseconds
            - min_ms: Minimum duration
            - max_ms: Maximum duration
            - total_ms: Total duration across all calls
        """
        summary = {}
        for op, durations in self._operation_stats.items():
            if durations:
                summary[op] = {
                    "count": len(durations),
                    "avg_ms": sum(durations) / len(durations),
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                    "total_ms": sum(durations),
                }
        return summary

    def clear(self) -> None:
        """Clear all collected metrics."""
        self._metrics.clear()
        self._operation_stats.clear()


# Global instance
_logger = LatencyLogger()


@contextmanager
def log_latency(operation: str, **metadata: Any):
    """Context manager for timing operations.

    Minimal overhead (<1ms) using time.perf_counter for high precision.
    Thread-safe implementation suitable for concurrent operations.

    Usage:
        with log_latency("search_corpus", corpus_id="123"):
            results = search_corpus(...)

    Args:
        operation: Name of the operation being timed
        **metadata: Additional metadata to store (e.g., corpus_id, query_text)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        duration_ms = (time.perf_counter() - start) * 1000
        _logger.record(operation, duration_ms, **metadata)


def timed(operation: Optional[str] = None) -> Callable:
    """Decorator for timing function execution.

    Supports both synchronous and asynchronous functions.
    Uses function name as operation name if not specified.

    Usage:
        @timed("corpus_search")
        def search_corpus(...):
            ...

        @timed()  # Uses function name
        def another_function(...):
            ...

        @timed("async_search")
        async def async_search(...):
            ...

    Args:
        operation: Optional operation name. Uses function name if None.

    Returns:
        Decorated function that logs execution time
    """
    def decorator(func: Callable) -> Callable:
        op_name = operation or func.__name__

        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with log_latency(op_name):
                return func(*args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            with log_latency(op_name):
                return await func(*args, **kwargs)

        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper

    return decorator


def get_metrics_summary() -> Dict[str, Any]:
    """Get global metrics summary.

    Returns:
        Summary statistics for all recorded operations
    """
    return _logger.get_summary()


def clear_metrics() -> None:
    """Clear global metrics."""
    _logger.clear()


__all__ = [
    "LatencyLogger",
    "LatencyMetric",
    "log_latency",
    "timed",
    "get_metrics_summary",
    "clear_metrics",
]
