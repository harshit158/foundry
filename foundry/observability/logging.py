import logging
import logging.config
from opentelemetry import _logs, trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from pythonjsonlogger.json import JsonFormatter

from rich.console import Console
from rich.logging import RichHandler

from .config import ObservabilityConfig

class AccessLogFilter(logging.Filter):
    """Custom logging filter to exclude certain endpoints from access logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Filter out log records for specified endpoints when log level is INFO or below.

        Args:
            record (logging.LogRecord): The log record to be filtered.

        Returns:
            bool: True if the log record should be processed, False otherwise.
        """
        
        # Inject OpenTelemetry trace/span ids
        span = trace.get_current_span()
        span_context = span.get_span_context()

        if span_context and span_context.trace_id != 0:
            record.trace_id = format(span_context.trace_id, "032x")
            record.span_id = format(span_context.span_id, "016x")
        else:
            record.trace_id = None
            record.span_id = None

        # Define the list of endpoints to exclude
        excluded_endpoints = ["/", "/favicon.ico", "/openapi.json"]
        
        # Check if the log level is INFO or below
        if record.levelno <= logging.INFO:
            # Ensure record.args exists and is a tuple with at least 3 elements
            if hasattr(record, "args") and isinstance(record.args, tuple) and len(record.args) >= 3:
                # Exclude logs for specified endpoints
                return record.args[2] not in excluded_endpoints
        # Allow logs for other levels
        return True

def get_rich_handler():
    console = Console(width=150)
    rich_handler = RichHandler(console=console, show_path=False, markup=False)
    return rich_handler

def get_otlp_handler():
    return LoggingHandler(level=logging.INFO, logger_provider=_logs.get_logger_provider())
    
# Create centralized logging configuration
def setup_logging(config: ObservabilityConfig):
    resource = Resource.create({"service.name": config.app_name})
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter()))
    _logs.set_logger_provider(logger_provider)

    handlers = ["console", "otlp"]
    
    logging_config = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {
                "format": "[trace=%(trace_id)s span=%(span_id)s] %(name)s : %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            },
            "json": {
                "()": JsonFormatter,
                "fmt": "%(asctime)s %(levelname)s %(name)s %(message)s %(trace_id)s %(span_id)s",
            }
        },
        "handlers": {
            "console": {
                "()": lambda: get_rich_handler(),
                "level": "INFO",
                "formatter": "standard",
                "filters": [AccessLogFilter()],
            },
            "otlp": {
                "()": lambda: get_otlp_handler(),
                "level": "INFO",
                "filters": [AccessLogFilter()],
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": handlers,
                "level": "INFO",
                "propagate": False,
            },
            "uvicorn.error": {"handlers": handlers, "level": "WARNING", "propagate": False},
            "uvicorn.access": {"handlers": handlers, "level": "INFO", "propagate": False},
            "httpx": {
                "handlers": handlers,
                "level": "WARNING",
                "propagate": False,
            },
            "httpcore": {
                "handlers": handlers,
                "level": "WARNING",
                "propagate": False,
            },
        },
    }

    logging.config.dictConfig(logging_config)


def get_logger(name):
    return logging.getLogger(name)
