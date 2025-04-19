from docx.shared import Cm


def check_margins(doc, filters: dict) -> list[dict]:
    """
    Проверяет верхнее, нижнее, левое и правое поля документа.
    Возвращает список ошибок с paragraph_index=0.
    """
    errors = []
    section = doc.sections[0]

    margin_fields = {
        "top_margin": section.top_margin.cm,
        "bottom_margin": section.bottom_margin.cm,
        "left_margin": section.left_margin.cm,
        "right_margin": section.right_margin.cm
    }

    for field, actual in margin_fields.items():
        expected = filters.get(field)
        if expected is not None:
            try:
                expected = float(expected)
                if round(actual, 2) != round(expected, 2):
                    errors.append({
                        "paragraph_index": 0,
                        "error": f"Неверное поле '{field}': ожидалось {expected} см, фактически {actual:.2f} см"
                    })
            except ValueError:
                errors.append({
                    "paragraph_index": 0,
                    "error": f"Неверное значение в шаблоне для '{field}'"
                })

    return errors
