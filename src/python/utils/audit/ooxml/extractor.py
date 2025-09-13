from __future__ import annotations

import os
import zipfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from lxml import etree
from docx.oxml.ns import qn

from . import W_NS


NS = {"w": W_NS}


@dataclass
class ParaProps:
    jc: Optional[str] = None  # left|center|right|both
    firstLine_twips: Optional[int] = None
    hanging_twips: Optional[int] = None
    left_twips: Optional[int] = None
    spacing_line_rule: Optional[str] = None  # auto|exact|atLeast
    spacing_line_units: Optional[int] = None
    pStyle: Optional[str] = None
    num_id: Optional[int] = None
    ilvl: Optional[int] = None


@dataclass
class RunProps:
    font_family: Optional[str] = None  # rFonts ascii/hAnsi
    size_hps: Optional[int] = None     # w:sz/@w:val
    caps: Optional[bool] = None        # presence of w:caps


@dataclass
class IRBlock:
    index: int
    text: str
    in_table: bool
    p_pr: ParaProps
    r_pr: RunProps
    p_style: Optional[str] = None
    heading_level: Optional[int] = None
    is_caption: Optional[str] = None  # 'figure'|'table'|None


@dataclass
class StylesCtx:
    p_style_ppr: Dict[str, ParaProps] = field(default_factory=dict)
    p_style_rpr: Dict[str, RunProps] = field(default_factory=dict)
    style_outline_lvl: Dict[str, int] = field(default_factory=dict)  # 0..n
    docdefaults_ppr: ParaProps = field(default_factory=ParaProps)
    docdefaults_rpr: RunProps = field(default_factory=RunProps)


@dataclass
class NumberingCtx:
    pass


@dataclass
class IR:
    blocks: List[IRBlock]
    styles: StylesCtx
    numbering: NumberingCtx
    sect_margins_twips: Optional[Dict[str, int]]


def _txt_of(el: etree._Element) -> str:
    parts = el.xpath('.//w:t', namespaces=NS)
    return ''.join((t.text or '') for t in parts)


def _para_props(p: etree._Element) -> ParaProps:
    pr = p.find('w:pPr', namespaces=NS)
    props = ParaProps()
    if pr is None:
        return props
    jc = pr.find('w:jc', namespaces=NS)
    if jc is not None:
        props.jc = jc.get(qn('w:val'))
    ind = pr.find('w:ind', namespaces=NS)
    if ind is not None:
        fl = ind.get(qn('w:firstLine'))
        hg = ind.get(qn('w:hanging'))
        lf = ind.get(qn('w:left'))
        props.firstLine_twips = int(fl) if fl is not None else None
        props.hanging_twips = int(hg) if hg is not None else None
        props.left_twips = int(lf) if lf is not None else None
    sp = pr.find('w:spacing', namespaces=NS)
    if sp is not None:
        props.spacing_line_rule = sp.get(qn('w:lineRule'))
        ln = sp.get(qn('w:line'))
        props.spacing_line_units = int(ln) if ln is not None else None
    st = pr.find('w:pStyle', namespaces=NS)
    if st is not None:
        props.pStyle = st.get(qn('w:val'))
    numpr = pr.find('w:numPr', namespaces=NS)
    if numpr is not None:
        numid = numpr.find('w:numId', namespaces=NS)
        ilvl = numpr.find('w:ilvl', namespaces=NS)
        if numid is not None:
            try:
                props.num_id = int(numid.get(qn('w:val')))
            except Exception:
                pass
        if ilvl is not None:
            try:
                props.ilvl = int(ilvl.get(qn('w:val')))
            except Exception:
                pass
    return props


def _dominant_run_props(p: etree._Element) -> RunProps:
    fam_counts: Dict[str, int] = {}
    size_counts: Dict[int, int] = {}
    caps_count = 0
    total_runs = 0
    for r in p.findall('w:r', namespaces=NS):
        total_runs += 1
        rpr = r.find('w:rPr', namespaces=NS)
        if rpr is None:
            continue
        rfonts = rpr.find('w:rFonts', namespaces=NS)
        if rfonts is not None:
            fam = rfonts.get(qn('w:ascii')) or rfonts.get(qn('w:hAnsi'))
            if fam:
                fam_counts[fam] = fam_counts.get(fam, 0) + 1
        sz = rpr.find('w:sz', namespaces=NS)
        if sz is not None:
            try:
                val = int(sz.get(qn('w:val')))
                size_counts[val] = size_counts.get(val, 0) + 1
            except Exception:
                pass
        if rpr.find('w:caps', namespaces=NS) is not None:
            caps_count += 1

    rp = RunProps()
    if fam_counts:
        rp.font_family = max(fam_counts.items(), key=lambda kv: kv[1])[0]
    if size_counts:
        rp.size_hps = max(size_counts.items(), key=lambda kv: kv[1])[0]
    if total_runs > 0:
        rp.caps = caps_count > 0
    return rp


def _parse_styles_from_bytes(data: bytes) -> StylesCtx:
    ctx = StylesCtx()
    tree = etree.fromstring(data)
    root = tree
    # docDefaults
    dd_ppr = root.find('.//w:docDefaults/w:pPrDefault/w:pPr', namespaces=NS)
    if dd_ppr is not None:
        ctx.docdefaults_ppr = _parse_ppr(dd_ppr)
    dd_rpr = root.find('.//w:docDefaults/w:rPrDefault/w:rPr', namespaces=NS)
    if dd_rpr is not None:
        ctx.docdefaults_rpr = _parse_rpr(dd_rpr)
    # paragraph styles
    for st in root.findall('w:style', namespaces=NS):
        if st.get(qn('w:type')) != 'paragraph':
            continue
        sid = st.get(qn('w:styleId'))
        if not sid:
            continue
        ppr = st.find('w:pPr', namespaces=NS)
        rpr = st.find('w:rPr', namespaces=NS)
        if ppr is not None:
            ctx.p_style_ppr[sid] = _parse_ppr(ppr)
        if rpr is not None:
            ctx.p_style_rpr[sid] = _parse_rpr(rpr)
        ol = st.find('w:outlineLvl', namespaces=NS)
        if ol is not None:
            try:
                ctx.style_outline_lvl[sid] = int(ol.get(qn('w:val')))
            except Exception:
                pass
    return ctx


def _parse_ppr(ppr: etree._Element) -> ParaProps:
    props = ParaProps()
    jc = ppr.find('w:jc', namespaces=NS)
    if jc is not None:
        props.jc = jc.get(qn('w:val'))
    ind = ppr.find('w:ind', namespaces=NS)
    if ind is not None:
        fl = ind.get(qn('w:firstLine'))
        hg = ind.get(qn('w:hanging'))
        lf = ind.get(qn('w:left'))
        props.firstLine_twips = int(fl) if fl is not None else None
        props.hanging_twips = int(hg) if hg is not None else None
        props.left_twips = int(lf) if lf is not None else None
    sp = ppr.find('w:spacing', namespaces=NS)
    if sp is not None:
        props.spacing_line_rule = sp.get(qn('w:lineRule'))
        ln = sp.get(qn('w:line'))
        props.spacing_line_units = int(ln) if ln is not None else None
    return props


def _parse_rpr(rpr: etree._Element) -> RunProps:
    rp = RunProps()
    rfonts = rpr.find('w:rFonts', namespaces=NS)
    if rfonts is not None:
        rp.font_family = rfonts.get(qn('w:ascii')) or rfonts.get(qn('w:hAnsi'))
    sz = rpr.find('w:sz', namespaces=NS)
    if sz is not None:
        try:
            rp.size_hps = int(sz.get(qn('w:val')))
        except Exception:
            pass
    if rpr.find('w:caps', namespaces=NS) is not None:
        rp.caps = True
    return rp


def _detect_caption_kind(text: str) -> Optional[str]:
    import re
    s = text.strip()
    if not s:
        return None
    if re.match(r"^Рис\.?\s*\d+", s, flags=re.IGNORECASE):
        return "figure"
    if re.match(r"^Табл(?:ица)?\.?\s*\d+", s, flags=re.IGNORECASE):
        return "table"
    return None


def _sect_margins(doc_root: etree._Element) -> Optional[Dict[str, int]]:
    sectPr = doc_root.find('.//w:body/w:sectPr', namespaces=NS)
    if sectPr is None:
        return None
    pgMar = sectPr.find('w:pgMar', namespaces=NS)
    if pgMar is None:
        return None
    out: Dict[str, int] = {}
    for k in ("top", "bottom", "left", "right"):
        v = pgMar.get(qn(f'w:{k}'))
        if v is not None:
            try:
                out[k] = int(v)
            except Exception:
                pass
    return out or None


def extract_ir(docx_path: str) -> IR:
    with zipfile.ZipFile(docx_path, 'r') as zf:
        with zf.open('word/document.xml') as f:
            doc_tree = etree.parse(f)
        doc_root = doc_tree.getroot()

        styles_ctx = StylesCtx()
        try:
            with zf.open('word/styles.xml') as sf:
                styles_ctx = _parse_styles_from_bytes(sf.read())
        except KeyError:
            pass

        # Numbering parsing omitted for MVP
        numbering_ctx = NumberingCtx()

        paragraphs = doc_root.xpath('//w:body//w:p', namespaces=NS)
        blocks: List[IRBlock] = []

        for idx, p in enumerate(paragraphs):
            text = _txt_of(p)
            in_table = bool(p.xpath('boolean(ancestor::w:tc)', namespaces=NS))
            ppr = _para_props(p)
            rpr = _dominant_run_props(p)
            p_style = ppr.pStyle

            heading_level: Optional[int] = None
            if p_style and p_style in styles_ctx.style_outline_lvl:
                heading_level = styles_ctx.style_outline_lvl[p_style] + 1
            elif ppr.ilvl is not None and ppr.ilvl in (0, 1, 2):
                heading_level = ppr.ilvl + 1

            is_caption = _detect_caption_kind(text)

            blocks.append(IRBlock(
                index=idx,
                text=text,
                in_table=in_table,
                p_pr=ppr,
                r_pr=rpr,
                p_style=p_style,
                heading_level=heading_level,
                is_caption=is_caption,
            ))

        margins = _sect_margins(doc_root)

        return IR(blocks=blocks, styles=styles_ctx, numbering=numbering_ctx, sect_margins_twips=margins)

