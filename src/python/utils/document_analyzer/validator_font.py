def check_font_rules(para, idx: int, rules: dict) -> list[dict]:
    errors = []
    for run in para.runs:
        font = run.font
        text = run.text

        # Шрифт
        if "font_name" in rules:
            allowed_fonts = rules["font_name"]
            if isinstance(allowed_fonts, str):
                allowed_fonts = [allowed_fonts]
            if font.name and font.name not in allowed_fonts:
                errors.append({
                    "paragraph_index": idx,
                    "error": f"Шрифт '{font.name}' вместо допустимого {allowed_fonts}"
                })

        # Размер шрифта
        if "font_size" in rules and font.size:
            allowed_sizes = rules["font_size"]
            if isinstance(allowed_sizes, (int, float)):
                allowed_sizes = [allowed_sizes]
            pt = font.size.pt
            if all(abs(pt - allowed) > 0.5 for allowed in allowed_sizes):
                errors.append({
                    "paragraph_index": idx,
                    "error": f"Размер шрифта {pt} pt, ожидался {allowed_sizes}"
                })

        # Цвет текста (RGB)
        if "font_color_rgb" in rules and font.color and font.color.rgb:
            actual = font.color.rgb.__str__().lower()
            expected = rules["font_color_rgb"].lower()
            if actual != expected:
                errors.append({
                    "paragraph_index": idx,
                    "error": f"Цвет текста {actual}, ожидался {expected}"
                })

        # Полужирный
        if "bold" in rules:
            actual_bold = font.bold if font.bold is not None else False
            if actual_bold != rules["bold"]:
                errors.append({
                    "paragraph_index": idx,
                    "error": f"Жирность: {actual_bold}, ожидалась: {rules['bold']}"
                })

        # Курсив
        if "italic" in rules:
            actual_italic = font.italic if font.italic is not None else False
            if actual_italic != rules["italic"]:
                errors.append({
                    "paragraph_index": idx,
                    "error": f"Курсив: {actual_italic}, ожидался: {rules['italic']}"
                })

        # Подчёркивание
        if "underline" in rules:
            actual_underline = font.underline if font.underline is not None else False
            if actual_underline != rules["underline"]:
                errors.append({
                    "paragraph_index": idx,
                    "error": f"Подчеркивание: {actual_underline}, ожидалось: {rules['underline']}"
                })

        # Заглавные буквы
        if "all_caps" in rules and rules["all_caps"]:
            if any(ch.islower() for ch in text if ch.isalpha()):
                errors.append({
                    "paragraph_index": idx,
                    "error": "Текст должен быть набран заглавными буквами"
                })

    return errors
