from __future__ import annotations

from typing import Dict, Any, Optional
from ..ooxml.resolve import resolve
from ..compare.numeric import eq_with_tol
from ..report.model import Issue


def check(block, ir, rule_id: str, mode: str, expected: Dict[str, Any]) -> Optional[Issue]:
    target = expected.get("eq")
    tol = expected.get("tol", 0)
    val = resolve(block, ir, 'font.size_hps', mode)
    ok = eq_with_tol(val.value, target, tol)
    if ok:
        return None
    msg = f"Размер шрифта: ожидалось {target}±{tol} hps, фактически {val.value or 'не задано'} (источник: {val.source})"
    return Issue(
        rule_id=rule_id,
        paragraph_index=block.index,
        code="FONT_SIZE",
        severity="error",
        message=msg,
        expected={"eq": target, "tol": tol},
        actual={"font.size_hps": val.value, "source": val.source},
    )

