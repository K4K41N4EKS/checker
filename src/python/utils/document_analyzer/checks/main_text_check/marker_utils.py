import re

def detect_marker(paragraph):
    match = re.match(r"^(\s*)([\d\w\-\u2022\u2013]+[.)]?)", paragraph.text.strip())
    return match.group(2) if match else None

def detect_marker_type(marker: str) -> str:
    if re.match(r"^\d+[.)]?$", marker):
        return "digit"
    elif re.match(r"^[A-Za-zА-Яа-я][.)]?$", marker):
        return "letter"
    elif marker in {"-", "–", "•"}:
        return "bullet"
    return "other"

def get_expected_list_level(paragraph, prev_marker_type, in_sublist, filters):
    text = paragraph.text.strip()
    marker = detect_marker(paragraph)
    if not marker:
        return "body_text", None, False

    marker_type = detect_marker_type(marker)
    ends_colon = text.endswith(":")

    indent = paragraph.paragraph_format.first_line_indent
    indent_cm = round(indent.cm, 2) if indent else 0.0

    indent_lvl1 = float(filters.get("list_level_1", {}).get("first_line_indent", 1.25))
    indent_lvl2 = float(filters.get("list_level_2", {}).get("first_line_indent", 1.75))

    if ends_colon:
        return "list_level_1", marker_type, True

    if in_sublist:
        if marker_type == prev_marker_type and abs(indent_cm - indent_lvl1) < 0.2:
            return "list_level_1", marker_type, False
        else:
            return "list_level_2", marker_type, True

    return ("list_level_1" if marker else "body_text"), marker_type, False
