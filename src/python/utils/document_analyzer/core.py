from docx import Document
from fastapi import HTTPException
from .template_parser import parse_template
from .toc_checker import find_start_index
from .checks.margin_check import check_margins
from .checks.main_text_check.core import check_main_text
from .checks.check_heading import check_headings
from .checks.page_numbering_check import check_page_numbering

def check_document_format(path: str, template_filters: dict) -> list[dict]:
    try:
        doc = Document(path)
    except Exception:
        raise HTTPException(status_code=400, detail="Не удалось открыть файл")

    filters = parse_template(template_filters)
    start_marker = filters.get("start_after_heading", "Оглавление")

    start_index = find_start_index(doc, start_marker, path)

    if start_index is None:
        return [{"paragraph_index": 0, "error": f"Раздел '{start_marker}' не найден"}]

    errors = []
    
    errors.extend(check_margins(doc, filters))
    errors.extend(check_headings(doc, start_index))
    errors.extend(check_page_numbering(path))
    errors.extend(check_main_text(doc, filters, start_index))

    return errors
