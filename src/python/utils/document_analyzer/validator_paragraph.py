from .helpers import is_paragraph_in_table

def check_paragraph_rules(para, idx: int, rules: dict) -> list[dict]:
    errors = []

    if not para.text.strip():
        return errors

    # Пока заголовки не валидируем
    if para.style and para.style.name.lower().startswith("heading"):
        return errors

    pf = para.paragraph_format

    if "first_line_indent" in rules:
        indent = pf.first_line_indent.cm if pf.first_line_indent else 0.0
        expected = rules["first_line_indent"]
        if abs(indent - expected) > 0.05:
            errors.append({
                "paragraph_index": idx,
                "error": f"Отступ первой строки {indent:.2f} см, ожидался {expected:.2f} см"
            })

    if "line_spacing" in rules:
        in_table = is_paragraph_in_table(para)
        expected_spacing = 1.0 if in_table else rules["line_spacing"]
        spacing = pf.line_spacing if pf.line_spacing else 1.0
        if abs(spacing - expected_spacing) > 0.1:
            errors.append({
                "paragraph_index": idx,
                "error": f"Межстрочный интервал {spacing}, ожидался {expected_spacing} {'в таблице' if in_table else ''}"
            })

    if "alignment" in rules:
        alignment = para.alignment.name if para.alignment else "LEFT"
        allowed = rules["alignment"]
        if isinstance(allowed, str):
            allowed = [allowed]
        if alignment.upper() not in [a.upper() for a in allowed]:
            errors.append({
                "paragraph_index": idx,
                "error": f"Выравнивание {alignment}, ожидалось: {allowed}"
            })

    return errors
