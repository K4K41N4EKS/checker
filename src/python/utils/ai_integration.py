from typing import Any, Dict


def notify_event(event: str, payload: Dict[str, Any] | None = None) -> None:
    """Placeholder hook for future AI-agent integration.

    Currently a no-op. Intended usage:
    - collect ambiguous cases
    - route to external analyzer
    - enrich results with suggestions
    """
    # TODO: wire to external AI service (HTTP/RPC) when available
    return None

