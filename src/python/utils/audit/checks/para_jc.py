from __future__ import annotations

from typing import Dict, Any, Optional
from ..ooxml.resolve import resolve
from ..compare.strings import one_of
from ..report.model import Issue


def check(block, ir, rule_id: str, mode: str, expected: Dict[str, Any]) -> Optional[Issue]:
    allowed = expected.get("oneOf") or []
    val = resolve(block, ir, 'para.jc', mode)
    ok = one_of(val.value, allowed)
    if ok:
        return None
    msg = f"Выравнивание: ожидалось {allowed}, фактически '{val.value or 'не задано'}' (источник: {val.source})"
    return Issue(
        rule_id=rule_id,
        paragraph_index=block.index,
        code="PARA_JC",
        severity="error",
        message=msg,
        expected={"oneOf": allowed},
        actual={"para.jc": val.value, "source": val.source},
    )

