from __future__ import annotations

from typing import Callable, Dict

from ..checks import para_jc, para_firstline, para_line, font_family, font_size, text_caps


CheckerFn = Callable[[object, object, str, str, dict], object | None]


REGISTRY: Dict[str, CheckerFn] = {
    "para.jc": para_jc.check,
    "para.firstLine_twips": para_firstline.check,
    "para.line": para_line.check,
    "font.family": font_family.check,
    "font.size_hps": font_size.check,
    "text.caps": text_caps.check,
}

