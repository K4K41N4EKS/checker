from __future__ import annotations

from typing import Dict, Any, List
from ..report.model import Issue


def check_document_margins(ir, expected: Dict[str, int], tol_twips: int, rule_id: str = "DOC-MARGINS") -> List[Issue]:
    issues: List[Issue] = []
    actual = ir.sect_margins_twips or {}
    for k in ("top", "bottom", "left", "right"):
        exp = expected.get(k)
        act = actual.get(k)
        if exp is None or act is None:
            continue
        if abs(int(act) - int(exp)) > int(tol_twips):
            msg = f"Поля страницы ({k}): ожидалось {exp}±{tol_twips} twips, фактически {act}"
            issues.append(Issue(
                rule_id=rule_id,
                paragraph_index=0,
                code=f"MARGIN_{k.upper()}",
                severity="error",
                message=msg,
                expected={k: exp, "tol": tol_twips},
                actual={k: act},
            ))
    return issues

