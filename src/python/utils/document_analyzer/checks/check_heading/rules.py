from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

def check_static_header(p, idx, label):
    return _validate_header(
        p, idx, label, title_case=True, all_caps=False
    )

def check_main_header_level_1(p, idx, label):
    return _validate_header(
        p, idx, label="Заголовок 1-го уровня", title_case=False, all_caps=True
    )

def check_main_header_level_2(p, idx, label):
    return _validate_header(
        p, idx, label="Заголовок 2-го уровня", title_case=False, all_caps=False
    )

def check_main_header_level_3(p, idx, label):
    return _validate_header(
        p, idx, label="Заголовок 3-го уровня", title_case=False, all_caps=False
    )

def _validate_header(p, idx, label, title_case=False, all_caps=False):
    errors = []
    text = p.text.strip()

    if title_case and not text.istitle():
        errors.append({"paragraph_index": idx, "error": f"{label}: Заголовок должен быть с заглавной буквы"})
    if all_caps and text.upper() != text:
        errors.append({"paragraph_index": idx, "error": f"{label} должен быть полностью заглавными буквами"})
    if not is_bold(p):
        errors.append({"paragraph_index": idx, "error": f"{label} должен быть жирным"})
    if get_alignment(p) != "center":
        errors.append({"paragraph_index": idx, "error": f"{label}: Выравнивание должно быть по центру"})
    if get_font(p) != "Times New Roman":
        errors.append({"paragraph_index": idx, "error": f"{label}: Шрифт должен быть Times New Roman"})
    if get_size(p) != 14:
        errors.append({"paragraph_index": idx, "error": f"{label}: Размер шрифта должен быть 14"})
    if get_spacing(p) != 1.5:
        errors.append({"paragraph_index": idx, "error": f"{label}: Межстрочный интервал должен быть 1.5"})
    if get_first_line_indent(p) != 0:
        errors.append({"paragraph_index": idx, "error": f"{label}: Абзацный отступ должен быть 0"})

    return errors

def is_bold(p):
    return any(run.bold for run in p.runs if run.text.strip())

def get_alignment(p):
    alignment = p.paragraph_format.alignment
    return "center" if alignment == WD_PARAGRAPH_ALIGNMENT.CENTER else "left"

def get_font(p):
    for run in p.runs:
        if run.font.name:
            return run.font.name
    return None

def get_size(p):
    for run in p.runs:
        if run.font.size:
            return round(run.font.size.pt)
    return None

def get_spacing(p):
    spacing = p.paragraph_format.line_spacing
    return round(spacing, 1) if spacing else None

def get_first_line_indent(p):
    indent = p.paragraph_format.first_line_indent
    return round(indent.cm, 2) if indent else 0.0
