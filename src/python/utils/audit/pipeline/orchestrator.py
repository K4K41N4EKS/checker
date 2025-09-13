from __future__ import annotations

from typing import Any, Dict, List, Tuple

from ..ooxml.extractor import extract_ir
from ..ir.scope import apply_scope
from ..pipeline.planner import plan
from ..rules.registry import REGISTRY
from ..report.model import Issue
from ..report.builders import issues_to_docx_comments
from ..checks.margins import check_document_margins
from ...docx_zip_comments import add_comments_to_docx_batch


def analyze_document(docx_path: str, compiled_rules: Dict[str, Any], *, emit_comments: bool = True, inplace: bool = True) -> Tuple[List[Issue], str]:
    # Extract IR
    ir = extract_ir(docx_path)

    # Document-level checks (margins)
    issues: List[Issue] = []
    document_cfg = (compiled_rules or {}).get('document') or {}
    margins_expected = document_cfg.get('margins_twips') or {}
    tol_twips = document_cfg.get('tolerance_twips', 5)
    if margins_expected:
        issues.extend(check_document_margins(ir, margins_expected, tol_twips))

    # Scope blocks
    scoped_blocks = apply_scope(ir.blocks, document_cfg)
    ir.blocks = scoped_blocks

    # Plan tasks
    tasks = plan(ir, (compiled_rules or {}).get('rules') or [])

    # Evaluate
    # Build quick index map for blocks by original paragraph index
    idx_map = {b.index: b for b in ir.blocks}

    for t in tasks:
        rule = t.rule
        mode = rule.get('mode') or 'effective'
        checks = rule.get('checks') or {}
        block = idx_map.get(t.block_index)
        if block is None:
            continue
        for key, exp in checks.items():
            checker = REGISTRY.get(key)
            if not checker:
                continue
            issue = checker(block, ir, rule_id=rule.get('id') or 'RULE', mode=mode, expected=exp)
            if issue is not None:
                issues.append(issue)

    # Emit comments
    output_path = docx_path
    if emit_comments and issues:
        try:
            comment_payload = issues_to_docx_comments(issues)
            output_path = add_comments_to_docx_batch(docx_path, comment_payload, inplace=inplace)
        except Exception:
            # Non-fatal
            pass

    return issues, output_path
