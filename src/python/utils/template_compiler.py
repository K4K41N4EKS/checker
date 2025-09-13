from __future__ import annotations

from typing import Any, Dict, Iterable, Optional
import math

# OOXML namespace (for reference)
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


# ---- Unit conversions ----
def cm_to_twips(cm: float | int | None) -> Optional[int]:
    """Convert centimeters to twips. 1 cm ≈ 567 twips (1440 / 2.54).

    Rounds to nearest integer. Returns None for None/NaN inputs.
    """
    if cm is None:
        return None
    try:
        v = float(cm)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    return int(round(v * 1440.0 / 2.54))


def pt_to_hps(pt: float | int | None) -> Optional[int]:
    """Convert points to half-points (hps). 1 pt → 2 hps.

    Rounds to nearest integer. Returns None for None/NaN inputs.
    """
    if pt is None:
        return None
    try:
        v = float(pt)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    return int(round(v * 2.0))


def line_multiple_to_units(mult: float | int | None) -> Optional[int]:
    """Convert line spacing multiplier to OOXML units: round(mult * 240).

    Example: 1.5 → 360
    """
    if mult is None:
        return None
    try:
        v = float(mult)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    return int(round(v * 240.0))


# ---- Mappings ----
_ALIGN_UI_TO_OOXML = {
    "left": "left",
    "center": "center",
    "right": "right",
    "justify": "both",
}


def map_alignment(ui_value: Optional[str]) -> Optional[str]:
    if not ui_value:
        return None
    return _ALIGN_UI_TO_OOXML.get(str(ui_value).strip().lower())


# ---- Defaults / tolerances ----
DEFAULT_TOL_TWIPS = 5   # ±5 twips for indents/margins
DEFAULT_TOL_HPS = 1     # ±1 hps (±0.5 pt)
DEFAULT_TOL_LINE_UNITS = 12  # ±12 for line multiple


def _present(value: Any) -> bool:
    """Return True if value is meaningfully provided (not None/NaN/empty)."""
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() != ""
    try:
        if isinstance(value, (int, float)) and math.isnan(float(value)):
            return False
    except Exception:
        pass
    return True


def _one_of(values: Iterable[Any]) -> Optional[list]:
    arr = [v for v in values if _present(v)]
    return arr if arr else None


def _get(block: Dict[str, Any], *keys: str) -> Any:
    """Return first present value for any of the keys."""
    for k in keys:
        if k in block and _present(block.get(k)):
            return block.get(k)
    return None


def _compile_para_checks(block: Dict[str, Any], *, tol_twips: int, tol_hps: int, tol_line: int) -> Dict[str, Any]:
    """Compile paragraph-level checks (alignment, first line, line spacing)."""
    checks: Dict[str, Any] = {}

    # Alignment
    jc = map_alignment(_get(block, "alignment", "text_align"))
    if _present(jc):
        checks["para.jc"] = {"oneOf": [jc]}

    # First line indents (positive firstLine, or hanging if negative)
    # UI may provide first line in cm as first_line_cm or first_line_indent
    first_line_tw = cm_to_twips(_get(block, "first_line_cm", "first_line_indent"))
    if _present(first_line_tw):
        checks["para.firstLine_twips"] = {"eq": int(first_line_tw), "tol": tol_twips}

    # Line spacing (multiple)
    mult_units = line_multiple_to_units(_get(block, "line_spacing", "line_multiple"))
    if _present(mult_units):
        line_mode = _get(block, "line_mode") or "multiple"  # multiple|exact|atLeast|any
        # When targeting multiple, OOXML uses lineRule="auto"
        line_rule = "auto" if line_mode == "multiple" else {
            "exact": "exact",
            "atLeast": "atLeast",
            "any": "any",
        }.get(str(line_mode), "auto")
        entry: Dict[str, Any] = {
            "lineRule": line_rule,
            "units": {"eq": int(mult_units), "tol": tol_line},
        }
        if line_mode and line_mode != "multiple":
            entry["mode"] = line_mode
        checks["para.line"] = entry

    return checks


def _compile_font_checks(block: Dict[str, Any], *, tol_hps: int) -> Dict[str, Any]:
    """Compile run-level font checks (family, size, caps)."""
    checks: Dict[str, Any] = {}

    # Family
    font_name = _get(block, "font_name", "font", "family")
    if _present(font_name):
        fams = _one_of([font_name])
        if fams:
            checks["font.family"] = {"oneOf": fams}

    # Size
    size_hps = pt_to_hps(_get(block, "font_size_pt", "font_size", "size_pt"))
    if _present(size_hps):
        checks["font.size_hps"] = {"eq": int(size_hps), "tol": tol_hps}

    # Caps
    if _get(block, "all_caps", "caps", "uppercase") is True:
        checks["text.caps"] = {"eq": "caps"}

    return checks


def _merge(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for d in dicts:
        if d:
            out.update(d)
    return out


def _compile_rule(rule_id: str, selector: Dict[str, Any], block: Dict[str, Any], *,
                  default_mode: str,
                  tol_twips: int,
                  tol_hps: int,
                  tol_line: int) -> Optional[Dict[str, Any]]:
    """Compile a single rule object from a UI block.

    Skips if block contains no recognized fields (nothing to validate).
    """
    para_checks = _compile_para_checks(block, tol_twips=tol_twips, tol_hps=tol_hps, tol_line=tol_line)
    font_checks = _compile_font_checks(block, tol_hps=tol_hps)
    checks = _merge(font_checks, para_checks)
    if not checks:
        return None

    mode = _get(block, "mode") or default_mode
    return {
        "id": rule_id,
        "selector": selector,
        "mode": mode,
        "checks": checks,
    }


def _margins_from_ui(ui: Dict[str, Any]) -> Optional[Dict[str, int]]:
    # Preferred nested form: margins_cm.{top,bottom,left,right}
    margins_cm = (ui or {}).get("margins_cm") or {}
    if isinstance(margins_cm, dict) and any(_present(margins_cm.get(k)) for k in ("top", "bottom", "left", "right")):
        return {k: int(cm_to_twips(margins_cm.get(k))) for k in ("top", "bottom", "left", "right") if _present(margins_cm.get(k))}

    # Flat form used in UI: top_margin/bottom_margin/...
    keys_map = {
        "top": _get(ui, "top_margin", "margin_top", "top"),
        "bottom": _get(ui, "bottom_margin", "margin_bottom", "bottom"),
        "left": _get(ui, "left_margin", "margin_left", "left"),
        "right": _get(ui, "right_margin", "margin_right", "right"),
    }
    if any(_present(v) for v in keys_map.values()):
        return {k: int(cm_to_twips(v)) for k, v in keys_map.items() if _present(v)}
    return None


def compile_ui_to_rules(ui: Dict[str, Any]) -> Dict[str, Any]:
    """Compile UI template JSON to normalized rule structure.

    Input example (minimal):
    {
      "margins_cm": {"top": 2.0, "bottom": 2.0, "left": 3.0, "right": 1.5},
      "h1": {"font_name":"Times New Roman","font_size_pt":16,"alignment":"center","first_line_cm":0,"line_spacing":1.5,"all_caps":true},
      "body": {"font_name":"Times New Roman","font_size_pt":14,"alignment":"justify","first_line_cm":1.25,"line_spacing":1.5}
    }
    """
    # Defaults and tolerances
    tol_twips = int(ui.get("tolerance_twips", DEFAULT_TOL_TWIPS))
    tol_hps = int(ui.get("tolerance_hps", DEFAULT_TOL_HPS))
    tol_line = int(ui.get("tolerance_line_units", DEFAULT_TOL_LINE_UNITS))
    default_mode = str(ui.get("mode", "effective"))  # effective | direct_only | style_only

    # Document margins
    margins_twips = _margins_from_ui(ui)

    document: Dict[str, Any] = {}
    if margins_twips:
        document["margins_twips"] = {k: int(v) for k, v in margins_twips.items()}
        document["tolerance_twips"] = tol_twips

    # Optional scope configuration (e.g., start_after_heading)
    if _present(ui.get("start_after_heading")):
        document.setdefault("scope", {})["start_after_heading"] = ui.get("start_after_heading")
    if isinstance(ui.get("static_headings"), list):
        document.setdefault("scope", {})["static_headings"] = ui.get("static_headings")
    if _present(ui.get("ai_integration_enabled")):
        document["ai_integration_enabled"] = bool(ui.get("ai_integration_enabled"))

    rules: list[Dict[str, Any]] = []

    # Headings H1..H3
    for level_key, level_num in (("h1", 1), ("h2", 2), ("h3", 3)):
        block = ui.get(level_key)
        if isinstance(block, dict):
            rule = _compile_rule(
                rule_id=f"H{level_num}-FORMAT",
                selector={"type": "heading", "level": level_num},
                block=block,
                default_mode=default_mode,
                tol_twips=tol_twips,
                tol_hps=tol_hps,
                tol_line=tol_line,
            )
            if rule:
                rules.append(rule)

    # Body paragraphs (outside tables by default)
    # Accept alternate UI keys for same semantics
    if not ui.get("h1") and isinstance(ui.get("main_header_level_1"), dict):
        ui["h1"] = ui.get("main_header_level_1")
    if not ui.get("h2") and isinstance(ui.get("main_header_level_2"), dict):
        ui["h2"] = ui.get("main_header_level_2")
    if not ui.get("h3") and isinstance(ui.get("main_header_level_3"), dict):
        ui["h3"] = ui.get("main_header_level_3")

    # Body paragraphs (outside tables by default)
    body = ui.get("body") or ui.get("body_text")
    if isinstance(body, dict):
        rule = _compile_rule(
            rule_id="BODY-FORMAT",
            selector={"type": "paragraph", "inTables": False},
            block=body,
            default_mode=default_mode,
            tol_twips=tol_twips,
            tol_hps=tol_hps,
            tol_line=tol_line,
        )
        if rule:
            rules.append(rule)

    # Text inside table cells
    table_cell = ui.get("table_cell_text")
    if isinstance(table_cell, dict):
        rule = _compile_rule(
            rule_id="TABLE-CELL-FORMAT",
            selector={"type": "paragraph", "inTables": True},
            block=table_cell,
            default_mode=default_mode,
            tol_twips=tol_twips,
            tol_hps=tol_hps,
            tol_line=tol_line,
        )
        if rule:
            rules.append(rule)

    # Captions (figure/table)
    fig = ui.get("figure_caption")
    if isinstance(fig, dict):
        rule = _compile_rule(
            rule_id="FIGURE-CAPTION-FORMAT",
            selector={"type": "caption", "kind": "figure"},
            block=fig,
            default_mode=default_mode,
            tol_twips=tol_twips,
            tol_hps=tol_hps,
            tol_line=tol_line,
        )
        if rule:
            rules.append(rule)
    tab = ui.get("table_caption")
    if isinstance(tab, dict):
        rule = _compile_rule(
            rule_id="TABLE-CAPTION-FORMAT",
            selector={"type": "caption", "kind": "table"},
            block=tab,
            default_mode=default_mode,
            tol_twips=tol_twips,
            tol_hps=tol_hps,
            tol_line=tol_line,
        )
        if rule:
            rules.append(rule)

    # Lists (levels 1..2)
    lst1 = ui.get("list_level_1")
    if isinstance(lst1, dict):
        rule = _compile_rule(
            rule_id="LIST1-FORMAT",
            selector={"type": "list", "level": 1},
            block=lst1,
            default_mode=default_mode,
            tol_twips=tol_twips,
            tol_hps=tol_hps,
            tol_line=tol_line,
        )
        if rule:
            rules.append(rule)
    lst2 = ui.get("list_level_2")
    if isinstance(lst2, dict):
        rule = _compile_rule(
            rule_id="LIST2-FORMAT",
            selector={"type": "list", "level": 2},
            block=lst2,
            default_mode=default_mode,
            tol_twips=tol_twips,
            tol_hps=tol_hps,
            tol_line=tol_line,
        )
        if rule:
            rules.append(rule)

    # Optional static header (treated as a special paragraph role)
    static_hdr = ui.get("static_header")
    if isinstance(static_hdr, dict):
        rule = _compile_rule(
            rule_id="STATIC-HEADER-FORMAT",
            selector={"type": "paragraph", "role": "static_header"},
            block=static_hdr,
            default_mode=default_mode,
            tol_twips=tol_twips,
            tol_hps=tol_hps,
            tol_line=tol_line,
        )
        if rule:
            rules.append(rule)

    return {
        "document": document,
        "rules": rules,
    }


__all__ = [
    "W_NS",
    "cm_to_twips",
    "pt_to_hps",
    "line_multiple_to_units",
    "map_alignment",
    "compile_ui_to_rules",
]
