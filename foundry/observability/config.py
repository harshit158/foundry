"""Configuration for observability components."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ObservabilityConfig:
    """Configuration for logging and tracing observability features.
    
    This dataclass encapsulates settings needed to initialize the observability
    package, allowing client applications to pass configuration explicitly rather
    than requiring the package to import settings from a fixed location.
    
    Attributes:
        app_name: The name of the application/service, used as the OpenTelemetry
                 service name in resource attributes for logging and tracing.
    """
    
    app_name: str
