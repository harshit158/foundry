"""
Token usage and cost helpers for LLM calls.

Usage metadata is captured with LangChain's ``get_usage_metadata_callback()``;
this module converts the resulting callback object into input/output tokens
and an estimated cost.
"""

from dataclasses import dataclass, field
from enum import Enum, StrEnum
from typing import Any


class Model(StrEnum):
    """LLM models available in Foundry.

    Add new models here and in ``MODEL_PRICING_USD_PER_1M`` as they are added
    to the codebase.
    """

    GPT_54_NANO = "gpt-5.4-nano"
    GPT_54_MINI = "gpt-5.4-mini"

# Token pricing per 1M tokens (USD). Update with actual provider pricing as needed.
MODEL_PRICING_USD_PER_1M: dict[str, dict[str, float]] = {
    Model.GPT_54_MINI: {"input": 0.75, "output": 4.5},
    Model.GPT_54_NANO: {"input": 0.2, "output": 1.25},
}


@dataclass
class UsageCost:
    """Aggregated token usage and estimated cost across LLM calls.

    Attributes:
        model: The last model seen; use ``per_model`` for the full breakdown.
        input_tokens: Total input tokens across all models.
        output_tokens: Total output tokens across all models.
        total_tokens: Total tokens (input + output) across all models.
        cost: Estimated cost in USD, or ``None`` if pricing is unavailable.
        per_model: Per-model breakdown keyed by model name.
    """

    model: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost: float | None = None
    per_model: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def cost_str(self) -> str:
        """Human-readable cost, e.g. ``$0.000450`` or ``unknown``."""
        if self.cost is None:
            return "unknown (no pricing configured)"
        return f"${self.cost:.6f}"


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float | None:
    """Estimate request cost in USD from token usage.

    Returns ``None`` when pricing for the given model is not configured.
    """
    pricing = MODEL_PRICING_USD_PER_1M.get(model)
    if pricing is None:
        return None
    return (input_tokens / 1_000_000) * pricing["input"] + (output_tokens / 1_000_000) * pricing["output"]


def get_usage_cost(usage_cb) -> UsageCost:
    """Extract input/output tokens and estimated cost from a usage callback.

    Args:
        usage_cb: The callback object yielded by
            ``langchain_core.callbacks.get_usage_metadata_callback()`` (an
            instance of ``UsageMetadataCallbackHandler``). It exposes a
            ``usage_metadata`` dict keyed by model name, where each value is a
            ``UsageMetadata`` dict with ``input_tokens`` / ``output_tokens`` /
            ``total_tokens``.

    Returns:
        An aggregated ``UsageCost`` with a per-model breakdown in ``per_model``.
    """
    result = UsageCost()
    total_cost = 0.0
    has_any_cost = False

    for model, usage in usage_cb.usage_metadata.items():
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)
        cost = estimate_cost(model, input_tokens, output_tokens)

        if cost is not None:
            total_cost += cost
            has_any_cost = True

        result.model = model
        result.input_tokens += input_tokens
        result.output_tokens += output_tokens
        result.total_tokens += total_tokens
        result.per_model[model] = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "cost": cost,
        }

    result.cost = total_cost if has_any_cost else None
    return result
