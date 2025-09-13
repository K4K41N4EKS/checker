from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List

from ..ooxml.extractor import IR
from ..rules.selectors import match_selector


@dataclass
class Task:
    rule: Dict[str, Any]
    block_index: int


def plan(ir: IR, rules: List[Dict[str, Any]]) -> List[Task]:
    tasks: List[Task] = []
    for rule in rules:
        selector = rule.get('selector') or {}
        for b in ir.blocks:
            if match_selector(b, selector):
                tasks.append(Task(rule=rule, block_index=b.index))
    return tasks

