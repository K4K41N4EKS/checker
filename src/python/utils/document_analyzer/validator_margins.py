def check_margins(doc, filters: dict) -> list[dict]:
    errors = []
    margins = filters.get("margins", {})

    if not doc.sections:
        return []

    section = doc.sections[0]
    actual = {
        "top": section.top_margin.cm,
        "bottom": section.bottom_margin.cm,
        "left": section.left_margin.cm,
        "right": section.right_margin.cm
    }

    for key, actual_val in actual.items():
        expected_val = margins.get(key)
        if expected_val and abs(actual_val - expected_val) > 0.1:
            errors.append({
                "paragraph_index": 0,
                "error": f"Поле {key}: {actual_val:.2f} см, ожидалось {expected_val:.2f} см"
            })

    return errors
