from __future__ import annotations

import math
from typing import Optional


def cm_to_twips(cm: float | int | None) -> Optional[int]:
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
    if mult is None:
        return None
    try:
        v = float(mult)
    except (TypeError, ValueError):
        return None
    if math.isnan(v):
        return None
    return int(round(v * 240.0))

