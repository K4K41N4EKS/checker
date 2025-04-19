from docx.shared import Cm

def get_indent_cm(paragraph):
    """Получает отступ первой строки в см, включая стиль."""
    indent = paragraph.paragraph_format.first_line_indent
    if indent is None and paragraph.style and paragraph.style.paragraph_format:
        indent = paragraph.style.paragraph_format.first_line_indent

    return round(indent.cm, 2) if indent else 0.0

def check_indent(p, text_filters: dict, paragraph_index: int) -> list[dict]:
    errors = []

    expected_indent = text_filters.get("first_line_indent")
    if expected_indent is None:
        return errors

    try:
        expected_indent = float(expected_indent)
    except (ValueError, TypeError):
        return errors

    actual_indent = get_indent_cm(p)

    if abs(actual_indent - expected_indent) > 0.1:
        errors.append({
            "paragraph_index": paragraph_index,
            "error": f"Абзацный отступ: ожидалось {expected_indent} см, получено {actual_indent} см"
        })

    return errors
