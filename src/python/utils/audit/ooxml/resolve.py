from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Tuple

from .extractor import IR, IRBlock, ParaProps, RunProps


@dataclass
class ValueWithSource:
    value: Any
    source: str  # 'direct' | 'style' | 'default' | 'none'


def _choose(first: Optional[Any], second: Optional[Any], third: Optional[Any]) -> tuple[Optional[Any], str]:
    if first is not None:
        return first, 'direct'
    if second is not None:
        return second, 'style'
    if third is not None:
        return third, 'default'
    return None, 'none'


def resolve(block: IRBlock, ir: IR, key: str, mode: str = 'effective') -> ValueWithSource:
    """Resolve property value for given block according to mode.

    Supported keys: 'para.jc', 'para.firstLine_twips', 'para.line', 'font.family', 'font.size_hps', 'text.caps'
    """
    # Style props for paragraph
    style_ppr: Optional[ParaProps] = None
    style_rpr: Optional[RunProps] = None
    if block.p_style:
        style_ppr = ir.styles.p_style_ppr.get(block.p_style)
        style_rpr = ir.styles.p_style_rpr.get(block.p_style)

    if key == 'para.jc':
        direct = block.p_pr.jc
        style = style_ppr.jc if style_ppr else None
        default = ir.styles.docdefaults_ppr.jc
        val, src = _choose(direct, style, default)
        if mode == 'direct_only':
            val, src = (direct, 'direct') if direct is not None else (None, 'none')
        elif mode == 'style_only':
            val, src = (style, 'style') if style is not None else (None, 'none')
        return ValueWithSource(val, src)

    if key == 'para.firstLine_twips':
        # Compute effective first-line offset relative to margin: left + firstLine - hanging
        def resolve_chain(vals: Tuple[Optional[int], Optional[int], Optional[int]]) -> Tuple[Optional[int], str, int]:
            d, s, df = vals
            if d is not None:
                return d, 'direct', 3
            if s is not None:
                return s, 'style', 2
            if df is not None:
                return df, 'default', 1
            return None, 'none', 0

        left_d = block.p_pr.left_twips
        left_s = style_ppr.left_twips if style_ppr else None
        left_df = ir.styles.docdefaults_ppr.left_twips
        fl_d = block.p_pr.firstLine_twips
        fl_s = style_ppr.firstLine_twips if style_ppr else None
        fl_df = ir.styles.docdefaults_ppr.firstLine_twips
        hg_d = block.p_pr.hanging_twips
        hg_s = style_ppr.hanging_twips if style_ppr else None
        hg_df = ir.styles.docdefaults_ppr.hanging_twips

        if mode == 'direct_only':
            if fl_d is None and hg_d is None and left_d is None:
                return ValueWithSource(None, 'none')
            left_v = left_d or 0
            fl_v = fl_d or 0
            hg_v = hg_d or 0
            return ValueWithSource(left_v + fl_v - hg_v, 'direct')
        elif mode == 'style_only':
            if fl_s is None and hg_s is None and left_s is None:
                return ValueWithSource(None, 'none')
            left_v = left_s or 0
            fl_v = fl_s or 0
            hg_v = hg_s or 0
            return ValueWithSource(left_v + fl_v - hg_v, 'style')
        else:
            left_v, left_src, left_lvl = resolve_chain((left_d, left_s, left_df))
            fl_v, fl_src, fl_lvl = resolve_chain((fl_d, fl_s, fl_df))
            hg_v, hg_src, hg_lvl = resolve_chain((hg_d, hg_s, hg_df))
            result = (left_v or 0) + (fl_v or 0) - (hg_v or 0)
            lvl = max(left_lvl if (left_v is not None) else 0,
                      fl_lvl if (fl_v is not None) else 0,
                      hg_lvl if (hg_v is not None) else 0)
            if lvl == 0:
                return ValueWithSource(None, 'none')
            src = 'default'
            if lvl == 3:
                src = 'direct'
            elif lvl == 2:
                src = 'style'
            return ValueWithSource(result, src)

    if key == 'para.line':
        direct = (block.p_pr.spacing_line_rule, block.p_pr.spacing_line_units)
        style = None
        if style_ppr:
            style = (style_ppr.spacing_line_rule, style_ppr.spacing_line_units)
        default = (ir.styles.docdefaults_ppr.spacing_line_rule,
                   ir.styles.docdefaults_ppr.spacing_line_units)
        if mode == 'direct_only':
            val = direct if any(direct) else None
            src = 'direct' if val is not None else 'none'
        elif mode == 'style_only':
            val = style if any(style or (None, None)) else None
            src = 'style' if val is not None else 'none'
        else:
            if any(direct):
                val, src = direct, 'direct'
            elif any(style or (None, None)):
                val, src = style, 'style'
            elif any(default):
                val, src = default, 'default'
            else:
                val, src = None, 'none'
        return ValueWithSource(val, src)

    if key == 'font.family':
        direct = block.r_pr.font_family
        style = style_rpr.font_family if style_rpr else None
        default = ir.styles.docdefaults_rpr.font_family
        val, src = _choose(direct, style, default)
        if mode == 'direct_only':
            val, src = (direct, 'direct') if direct is not None else (None, 'none')
        elif mode == 'style_only':
            val, src = (style, 'style') if style is not None else (None, 'none')
        return ValueWithSource(val, src)

    if key == 'font.size_hps':
        direct = block.r_pr.size_hps
        style = style_rpr.size_hps if style_rpr else None
        default = ir.styles.docdefaults_rpr.size_hps
        val, src = _choose(direct, style, default)
        if mode == 'direct_only':
            val, src = (direct, 'direct') if direct is not None else (None, 'none')
        elif mode == 'style_only':
            val, src = (style, 'style') if style is not None else (None, 'none')
        return ValueWithSource(val, src)

    if key == 'text.caps':
        direct = block.r_pr.caps
        style = style_rpr.caps if style_rpr else None
        default = ir.styles.docdefaults_rpr.caps
        val, src = _choose(direct, style, default)
        if mode == 'direct_only':
            val, src = (direct, 'direct') if direct is not None else (None, 'none')
        elif mode == 'style_only':
            val, src = (style, 'style') if style is not None else (None, 'none')
        return ValueWithSource(val, src)

    return ValueWithSource(None, 'none')

