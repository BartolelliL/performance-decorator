"""Measure and report function execution time."""

from __future__ import annotations

import inspect
from functools import wraps
from time import perf_counter
from typing import Any, Callable, List, NamedTuple, Optional, TypeVar, cast

F = TypeVar("F", bound=Callable[..., Any])


class Timing(NamedTuple):
    """The data passed to ``on_complete`` after a decorated call."""

    function_name: str
    duration: float
    succeeded: bool
    exception: Optional[BaseException]


def performance(
    function: Optional[F] = None,
    *,
    history_size: int = 1,
    log: Optional[Callable[[str], Any]] = print,
    on_complete: Optional[Callable[[Timing], Any]] = None,
) -> Any:
    """Measure a function with one simple, configurable decorator.

    Use ``@performance`` for the defaults, or ``@performance(...)`` to
    customize it. Every duration is measured in seconds with
    :func:`time.perf_counter`.

    Args:
        history_size: Maximum number of durations kept in
            ``wrapped.execution_times``. The default is ``1``. Set it to
            ``0`` to disable history and keep only ``last_duration``.
        log: A callable receiving the message printed after each call, such
            as ``logger.info``. Use ``None`` to disable output.
        on_complete: An optional callable receiving a ``Timing`` object after
            every completed call. It includes ``function_name``, ``duration``,
            ``succeeded``, and ``exception`` for sending metrics anywhere.

    The wrapped function keeps its name, docstring, arguments, and return
    value. Its latest duration is available as ``wrapped.last_duration``;
    bounded history is available as ``wrapped.execution_times``. Timing is
    recorded for failed calls too, and ``async def`` functions are supported.

    Example:
        ``@performance(history_size=10, log=logger.info,
        on_complete=save_metric)``
    """
    if function is None:
        return lambda decorated: performance(
            decorated,
            history_size=history_size,
            log=log,
            on_complete=on_complete,
        )
    if history_size < 0:
        raise ValueError("history_size must be greater than or equal to zero")

    execution_times: List[float] = []

    def record(duration: float, exception: Optional[BaseException]) -> None:
        timed.last_duration = duration  # type: ignore[attr-defined]
        if history_size:
            execution_times.append(duration)
            del execution_times[:-history_size]
        timed.execution_times = execution_times  # type: ignore[attr-defined]
        result = Timing(function.__name__, duration, exception is None, exception)
        if log is not None:
            log(f"{function.__name__} took {duration:.6f} seconds")
        if on_complete is not None:
            on_complete(result)

    if inspect.iscoroutinefunction(function):
        @wraps(function)
        async def timed(*args: Any, **kwargs: Any) -> Any:
            start = perf_counter()
            exception = None
            try:
                return await function(*args, **kwargs)
            except BaseException as error:
                exception = error
                raise
            finally:
                record(perf_counter() - start, exception)
    else:
        @wraps(function)
        def timed(*args: Any, **kwargs: Any) -> Any:
            start = perf_counter()
            exception = None
            try:
                return function(*args, **kwargs)
            except BaseException as error:
                exception = error
                raise
            finally:
                record(perf_counter() - start, exception)

    timed.last_duration = None  # type: ignore[attr-defined]
    timed.execution_times = execution_times  # type: ignore[attr-defined]
    return cast(F, timed)


__all__ = ["Timing", "performance"]
