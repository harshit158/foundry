from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import ObservabilityConfig

def setup_tracing(config: ObservabilityConfig):
    resource = Resource.create({"service.name": config.app_name})
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    exporter = OTLPSpanExporter()

    span_processor = BatchSpanProcessor(exporter)
    provider.add_span_processor(span_processor)


def get_tracer(name: str):
    return trace.get_tracer(name)