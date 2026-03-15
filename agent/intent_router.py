"""Intent routing — Phase 0 stub.

In Phase 0 every query is routed directly to the Sonnet LLM.
Future phases will use a lightweight model (e.g. Haiku) to classify
intents and route simple queries to faster/cheaper models.
"""

from __future__ import annotations


async def route_intent(text: str) -> str:
    """Classify user intent and return the target model tier.

    Returns
    -------
    str
        ``"sonnet"`` — always, in Phase 0.
    """
    _ = text  # unused in Phase 0
    return "sonnet"
