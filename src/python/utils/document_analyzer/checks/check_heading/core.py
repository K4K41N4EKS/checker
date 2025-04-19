from docx.document import Document
from .validators import (
    is_main_header_lvl_1, is_main_header_lvl_2, is_main_header_lvl_3
)
from .rules import (
    check_static_header, check_main_header_level_1,
    check_main_header_level_2, check_main_header_level_3
)

def check_headings(doc: Document, start_index: int) -> list[dict]:
    errors = []
    paragraphs = doc.paragraphs[start_index:]

    after_vvedenie = False

    for i, p in enumerate(paragraphs):
        text = p.text.strip()
        global_index = start_index + i

        if not text:
            continue

        if not after_vvedenie:
            if text.lower() == "введение":
                after_vvedenie = True
                errors.extend(check_static_header(p, global_index, text))
            continue

        if text.lower() in {"заключение", "список использованных источников"}:
            errors.extend(check_static_header(p, global_index, text))
        elif is_main_header_lvl_1(text):
            errors.extend(check_main_header_level_1(p, global_index, text))
        elif is_main_header_lvl_2(text):
            errors.extend(check_main_header_level_2(p, global_index, text))
        elif is_main_header_lvl_3(text):
            errors.extend(check_main_header_level_3(p, global_index, text))

    return errors
