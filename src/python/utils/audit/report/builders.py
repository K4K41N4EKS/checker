from __future__ import annotations

from typing import List, Dict, Any
from .model import Issue


def issues_to_api(issues: List[Issue]) -> List[Dict[str, Any]]:
    return [i.to_dict() for i in issues]


def issues_to_docx_comments(issues: List[Issue]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for i in issues:
        out.append({
            "paragraph_index": i.paragraph_index,
            "error": i.message,
            "code": i.code,
            "category": "format",
            "severity": i.severity,
            "meta": {"rule_id": i.rule_id, "expected": i.expected, "actual": i.actual},
        })
    return out

