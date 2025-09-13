from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict


@dataclass
class Issue:
    rule_id: str
    paragraph_index: int
    message: str
    code: str = "RULE_VIOLATION"
    severity: str = "error"  # error|warning|info
    expected: Dict[str, Any] | None = None
    actual: Dict[str, Any] | None = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

