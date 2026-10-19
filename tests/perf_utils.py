import statistics
import time
from typing import Callable, Tuple, TypeVar
from unittest import TestCase

T = TypeVar("T")


def assert_near_linear(
    test_case: TestCase,
    operation: Callable[[int], T],
    small_size: int,
    large_size: int,
    *,
    max_growth: float = 3.5,
    noise_seconds: float = 0.02,
    warmup_size: int = 200,
) -> Tuple[T, T]:
    """Assert that doubling adversarial input has bounded time growth."""
    if small_size < 1 or large_size <= small_size:
        raise ValueError("sizes must be positive and increasing")

    operation(warmup_size)
    small_result, small_elapsed = _measure(operation, small_size)
    large_result, large_elapsed = _measure(operation, large_size)
    test_case.assertLess(
        large_elapsed,
        small_elapsed * max_growth + noise_seconds,
        f"time growth {large_elapsed / max(small_elapsed, 1e-12):.2f}x exceeded {max_growth:.2f}x",
    )
    return small_result, large_result


def _measure(operation: Callable[[int], T], size: int) -> Tuple[T, float]:
    timings = []
    result = operation(size)
    for _ in range(3):
        started = time.perf_counter()
        result = operation(size)
        timings.append(time.perf_counter() - started)
    return result, statistics.median(timings)
