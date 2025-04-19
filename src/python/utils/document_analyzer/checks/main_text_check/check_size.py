def check_size(paragraph, filters, index):
    errors = []
    actual_size = next((r.font.size.pt for r in paragraph.runs if r.font.size), None)
    if not actual_size and paragraph.style.font.size:
        actual_size = paragraph.style.font.size.pt

    expected_size = filters.get("font_size")
    if expected_size and actual_size and round(actual_size, 1) != round(float(expected_size), 1):
        errors.append({
            "paragraph_index": index,
            "error": f"Размер шрифта: ожидалось {expected_size}, найдено {actual_size:.1f}"
        })
    return errors
