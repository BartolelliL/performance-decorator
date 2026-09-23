"""Measure and report function execution time."""

from __future__ import annotations

from functools import wraps
from time import perf_counter
from typing import Any, Callable, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


def performance(function: F) -> F:
    """Decorate a function to print and expose its execution time.

    The wrapped function keeps its original return value. Its most recent
    execution time, in seconds, is available as ``function.last_duration``.
    A history of all completed calls is available as
    ``function.execution_times``.
    """

    @wraps(function)
    def timed(*args: Any, **kwargs: Any) -> Any:
        start = perf_counter()
        try:
            return function(*args, **kwargs)
        finally:
            duration = perf_counter() - start
            timed.last_duration = duration  # type: ignore[attr-defined]
            timed.execution_times.append(duration)  # type: ignore[attr-defined]
            print(f"{function.__name__} took {duration:.6f} seconds")

    timed.last_duration = None  # type: ignore[attr-defined]
    timed.execution_times = []  # type: ignore[attr-defined]
    return cast(F, timed)


__all__ = ["performance"]
