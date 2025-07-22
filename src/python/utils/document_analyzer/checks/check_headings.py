import re
from .main_text_check.check_font import check_font
from .main_text_check.check_size import check_size
from .main_text_check.check_alignment import check_alignment
from .main_text_check.check_indent import check_indent
from .main_text_check.check_spacing import check_spacing

STATIC_HEADINGS = {"введение", "заключение", "список использованных источников"}
APPENDICES_MARKER = "приложения"


def check_headings(doc, start_index: int, filters: dict) -> list[dict]:
    errors = []
    after_intro = False

    for idx, p in enumerate(doc.paragraphs[start_index:], start=start_index):
        text = p.text.strip()
        if not text:
            continue

        if text.lower() == APPENDICES_MARKER:
            break

        if not after_intro:
            if text.lower() == "введение":
                after_intro = True
                errors.extend(
                    _check_heading_paragraph(
                        p, idx,
                        filters.get("static_header", {}),
                        label="Введение"
                    )
                )
            continue

        lower_text = text.lower()
        if lower_text in STATIC_HEADINGS:
            errors.extend(_check_heading_paragraph(p, idx, filters.get("static_header", {}), label=text))
        elif re.match(r'^\d+ ', text):
            errors.extend(_check_heading_paragraph(p, idx, filters.get("main_header_level_1", {}), label=text, level=1))
        elif re.match(r'^\d+\.\d+ ', text):
            errors.extend(_check_heading_paragraph(p, idx, filters.get("main_header_level_2", {}), label=text, level=2))
        elif re.match(r'^\d+\.\d+\.\d+ ', text):
            errors.extend(_check_heading_paragraph(p, idx, filters.get("main_header_level_3", {}), label=text, level=3))

    return errors


def _check_heading_paragraph(paragraph, index, expected_filter, label="", level=None) -> list[dict]:
    errors = []
    exp = dict(expected_filter) if expected_filter is not None else {}

    exp.setdefault("font_name", "Times New Roman")
    exp.setdefault("font_size", 14)
    exp.setdefault("alignment", "center")
    exp.setdefault("first_line_indent", 0.0)
    exp.setdefault("line_spacing", 1.5)

    if level == 1:
        exp.setdefault("all_caps", True)
        exp.setdefault("title_case", False)
    elif level in (2, 3):
        exp.setdefault("all_caps", False)
        exp.setdefault("title_case", False)
    else:
        exp.setdefault("all_caps", False)
        exp.setdefault("title_case", True)

    text = paragraph.text.strip()

    # Проверка регистра
    if exp.get("all_caps") and text and text.upper() != text:
        errors.append({
            "paragraph_index": index,
            "error": f"{label}: весь текст должен быть заглавными буквами"
        })

    # Альтернативная проверка жирности
    if not _paragraph_is_effectively_bold(paragraph):
        errors.append({
            "paragraph_index": index,
            "error": f"{label}: должен быть жирным (включая стиль)"
        })

    # Остальные проверки
    for check_func in (check_font, check_size, check_alignment, check_indent, check_spacing):
        for err in check_func(paragraph, exp, index):
            prefixed = f"{label}: {err['error'][0].lower() + err['error'][1:]}"
            errors.append({
                "paragraph_index": index,
                "error": prefixed
            })

    return errors


def _paragraph_is_effectively_bold(paragraph) -> bool:
    """Проверяет, жирный ли весь текст параграфа — напрямую или по стилю абзаца."""
    paragraph_style_bold = (
        paragraph.style
        and paragraph.style.font
        and paragraph.style.font.bold
    )

    for run in paragraph.runs:
        if not run.text.strip():
            continue
        # если явно жирный
        if run.bold is True:
            continue
        # если у run нет bold, но стиль абзаца жирный
        if run.bold is None and paragraph_style_bold:
            continue
        # если явно не жирный
        return False

    return True
