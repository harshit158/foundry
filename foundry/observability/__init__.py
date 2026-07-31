from .logging import get_logger, setup_logging
from .tracing import get_tracer, setup_tracing

_initialized = False

def init_observability():
    global _initialized

    if _initialized:
        return

    setup_tracing()
    setup_logging()
    _initialized = True


# Ensure logging and tracing are configured as soon as observability is imported.
init_observability()