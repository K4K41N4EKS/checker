def check_spacing(paragraph, text_filters, index):
    errors = []
    expected_spacing = text_filters.get("line_spacing")
    actual_spacing = None

    if paragraph.paragraph_format.line_spacing:
        actual_spacing = paragraph.paragraph_format.line_spacing
    elif paragraph.style.paragraph_format.line_spacing:
        actual_spacing = paragraph.style.paragraph_format.line_spacing

    if expected_spacing is not None and actual_spacing is not None:
        if round(actual_spacing, 1) != round(float(expected_spacing), 1):
            errors.append({
                "paragraph_index": index,
                "error": f"Межстрочный интервал: ожидалось {expected_spacing}, найдено {actual_spacing:.1f}"
            })
    return errors
