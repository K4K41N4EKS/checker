from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from .marker_utils import detect_marker

def check_alignment(p, text_filters: dict, paragraph_index: int) -> list[dict]:
    errors = []
    expected_alignment = text_filters.get("alignment")
    if not expected_alignment: 
        return errors

    align_map = {
        "left": WD_PARAGRAPH_ALIGNMENT.LEFT,
        "center": WD_PARAGRAPH_ALIGNMENT.CENTER,
        "right": WD_PARAGRAPH_ALIGNMENT.RIGHT,
        "justify": WD_PARAGRAPH_ALIGNMENT.JUSTIFY,
        "both": WD_PARAGRAPH_ALIGNMENT.JUSTIFY,
    }

    actual = p.paragraph_format.alignment
    if actual is None:
        if p.style and p.style.paragraph_format:
            actual = p.style.paragraph_format.alignment

    if actual is None:
        actual = WD_PARAGRAPH_ALIGNMENT.LEFT

    if detect_marker(p) and actual == WD_PARAGRAPH_ALIGNMENT.LEFT:
        return errors

    allowed = expected_alignment if isinstance(expected_alignment, list) else [expected_alignment]
    allowed_values = {align_map.get(a) for a in allowed if a in align_map}

    if actual not in allowed_values:
        readable = ", ".join(allowed)
        errors.append({
            "paragraph_index": paragraph_index,
            "error": f"Выравнивание: ожидалось {readable}"
        })

    return errors
