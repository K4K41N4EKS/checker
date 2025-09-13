from __future__ import annotations

from typing import Dict, Any, Optional
from ..ooxml.resolve import resolve
from ..report.model import Issue


def check(block, ir, rule_id: str, mode: str, expected: Dict[str, Any]) -> Optional[Issue]:
    exp = expected.get("eq")
    val = resolve(block, ir, 'text.caps', mode)
    ok = (exp == 'caps' and bool(val.value) is True) or (exp is None)
    if ok:
        return None
    msg = f"Режим 'все заглавными': ожидалось включено, фактически {('включено' if val.value else 'выключено') if val.value is not None else 'не задано'} (источник: {val.source})"
    return Issue(
        rule_id=rule_id,
        paragraph_index=block.index,
        code="TEXT_CAPS",
        severity="error",
        message=msg,
        expected={"eq": exp},
        actual={"text.caps": val.value, "source": val.source},
    )

