"""Reusable decorators and helper context managers for Belt Radar."""

# Standard Library
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from time import perf_counter

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)

_perf_sections: ContextVar[dict[str, float] | None] = ContextVar(
    "perf_sections", default=None
)


def timed_endpoint(label: str):
    """
        Measure total endpoint runtime and all nested timed sections.

            Example:
            @timed_endpoint("My Endpoint")
    def my_view(request):
        with timed_section("DB Queries"):
            # some database operations
        with timed_section("Processing"):
            # some data processing
    """

    def decorator(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            token = _perf_sections.set({})
            started = perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                total_ms = (perf_counter() - started) * 1000
                sections = _perf_sections.get() or {}
                section_text = " ".join(
                    f"{section}={duration:.2f}ms"
                    for section, duration in sorted(
                        sections.items(), key=lambda item: item[1], reverse=True
                    )
                )
                logger.info(
                    f"[Beltradar Perf] {label} total={total_ms:.2f}ms"
                    f"{(' ' + section_text) if section_text else ''}"
                )
                _perf_sections.reset(token)

        return wrapped

    return decorator


@contextmanager
def timed_section(name: str):
    """
        Measure one logical section inside a timed endpoint.

            Example:
    @timed_endpoint("My Endpoint")
    def my_view(request):
        with timed_section("DB Queries"):
            # some database operations
        with timed_section("Processing"):
            # some data processing
    """
    started = perf_counter()
    try:
        yield
    finally:
        sections = _perf_sections.get()
        if sections is not None:
            sections[name] = sections.get(name, 0.0) + (
                (perf_counter() - started) * 1000
            )
