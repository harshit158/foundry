from .config import ObservabilityConfig
from .logging import get_logger, setup_logging
from .tracing import get_tracer, setup_tracing

__all__ = ["ObservabilityConfig", "init_observability", "get_logger", "get_tracer"]


def init_observability(config: ObservabilityConfig) -> None:
    """Initialize logging and tracing with the provided configuration.
    
    This function should be called once at application startup to set up
    centralized observability (logging and tracing) using the provided config.
    
    Args:
        config: ObservabilityConfig instance with application settings.
    
    Example:
        from foundry.observability import init_observability, ObservabilityConfig
        
        config = ObservabilityConfig(app_name="my-service")
        init_observability(config)
        
        # Now use logging and tracing:
        logger = get_logger(__name__)
        tracer = get_tracer(__name__)
    """
    setup_tracing(config)
    setup_logging(config)