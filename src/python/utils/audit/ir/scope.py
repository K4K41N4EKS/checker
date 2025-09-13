from __future__ import annotations

from typing import List, Dict, Any

from ..ooxml.extractor import IRBlock


def apply_scope(blocks: List[IRBlock], document_cfg: Dict[str, Any] | None) -> List[IRBlock]:
    if not document_cfg:
        return blocks
    scope = (document_cfg or {}).get("scope") or {}
    start_after = scope.get("start_after_heading")
    if start_after:
        needle = str(start_after).strip().lower()
        start_idx = None
        for b in blocks:
            if b.heading_level and needle in (b.text or '').strip().lower():
                start_idx = b.index
                break
        if start_idx is not None:
            return [b for b in blocks if b.index >= start_idx]
    return blocks

