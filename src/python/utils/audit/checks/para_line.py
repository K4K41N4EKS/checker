from __future__ import annotations

from typing import Dict, Any, Optional
from ..ooxml.resolve import resolve
from ..compare.numeric import eq_with_tol
from ..report.model import Issue


def check(block, ir, rule_id: str, mode: str, expected: Dict[str, Any]) -> Optional[Issue]:
    """Check line spacing.

    expected example: {"lineRule":"auto","units":{"eq":360,"tol":12}, "mode":"multiple|exact|atLeast|any"}
    """
    exp_rule = expected.get("lineRule")
    exp_units_cfg = expected.get("units") or {}
    exp_units = exp_units_cfg.get("eq")
    exp_tol = exp_units_cfg.get("tol", 0)
    line_mode = expected.get("mode")  # may be None

    val = resolve(block, ir, 'para.line', mode)
    actual_rule, actual_units = (None, None)
    if isinstance(val.value, tuple) and len(val.value) == 2:
        actual_rule, actual_units = val.value

    # Rule acceptance
    rule_ok = True
    if line_mode == "multiple" or (line_mode is None and exp_rule == "auto"):
        rule_ok = (actual_rule == "auto")
    elif line_mode in ("exact", "atLeast"):
        rule_ok = (actual_rule == line_mode)
    elif line_mode == "any":
        rule_ok = True

    units_ok = eq_with_tol(actual_units, exp_units, exp_tol)
    if rule_ok and units_ok:
        return None

    msg_parts = []
    if not rule_ok:
        msg_parts.append(f"режим ожидался '{exp_rule}', фактически '{actual_rule or 'не задано'}'")
    if not units_ok:
        msg_parts.append(f"значение ожидалось {exp_units}±{exp_tol}, фактически {actual_units or 'не задано'}")
    msg = "Межстрочный интервал: " + ", ".join(msg_parts) + f" (источник: {val.source})"

    return Issue(
        rule_id=rule_id,
        paragraph_index=block.index,
        code="PARA_LINE",
        severity="error",
        message=msg,
        expected={"lineRule": exp_rule, "units": exp_units_cfg},
        actual={"lineRule": actual_rule, "units": actual_units, "source": val.source},
    )

