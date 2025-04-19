from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from .marker_utils import detect_marker, get_expected_list_level
from .check_font import check_font
from .check_size import check_size
from .check_alignment import check_alignment
from .check_indent import check_indent
from .check_spacing import check_spacing
from .block_utils import is_heading, is_picture_caption, is_table_caption

def check_main_text(doc, filters: dict, start_index: int) -> list[dict]:
    errors = []
    paragraphs = doc.paragraphs
    prev_was_picture = False
    in_sublist = False
    prev_marker_type = None

    for i, p in enumerate(paragraphs[start_index:], start=start_index):
        text = p.text.strip()
        if not text:
            in_sublist = False
            continue

        if is_heading(p):
            continue

        if is_table_caption(p):
            text_filters = filters.get("table_caption", {})
        elif is_picture_caption(p):
            text_filters = filters.get("figure_caption", {})
        elif prev_was_picture:
            text_filters = filters.get("figure_caption", {})
            prev_was_picture = False
        elif p._element.xpath(".//w:numPr") or detect_marker(p):
            level, prev_marker_type, in_sublist = get_expected_list_level(p, prev_marker_type, in_sublist, filters)
            text_filters = filters.get(level, {}) if level else filters.get("body_text", {})
        else:
            in_sublist = False
            text_filters = filters.get("body_text", {})

        errors += check_font(p, text_filters, i)
        errors += check_size(p, text_filters, i)
        errors += check_alignment(p, text_filters, i)
        errors += check_indent(p, text_filters, i)
        errors += check_spacing(p, text_filters, i)

        if "graphic" in p._element.xml:
            prev_was_picture = True

    return errors
