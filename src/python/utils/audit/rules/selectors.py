from __future__ import annotations

from typing import Dict, Any, TYPE_CHECKING
"""Selector matcher for IR blocks.

Matches compiled rules' selectors to extracted IR blocks.
"""


if TYPE_CHECKING:
    # Imported only for type checking to avoid runtime dependency/cycles
    from ..ooxml.extractor import IRBlock


def match_selector(block: IRBlock, selector: Dict[str, Any]) -> bool:
    t = selector.get("type")
    if t == "heading":
        level = selector.get("level")
        return block.heading_level == level
    if t == "paragraph":
        in_tables = selector.get("inTables")
        if in_tables is not None:
            if bool(block.in_table) != bool(in_tables):
                return False
        # role can be used for special paragraphs in future
        return True
    if t == "list":
        level = selector.get("level")
        if block.p_pr.num_id is None or block.p_pr.ilvl is None:
            return False
        return (block.p_pr.ilvl + 1) == level
    if t == "caption":
        kind = selector.get("kind")
        return block.is_caption == kind
    return False
