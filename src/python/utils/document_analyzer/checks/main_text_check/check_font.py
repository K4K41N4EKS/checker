def check_font(paragraph, filters, index):
    errors = []
    actual_font = next((r.font.name for r in paragraph.runs if r.font.name), None)
    if not actual_font:
        actual_font = paragraph.style.font.name

    expected_font = filters.get("font_name")
    if expected_font and actual_font and actual_font != expected_font:
        errors.append({
            "paragraph_index": index,
            "error": f"Шрифт: ожидалось {expected_font}, найдено {actual_font}"
        })
    return errors
