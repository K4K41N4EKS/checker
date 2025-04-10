from docx import Document
from src.python.utils.logger_utils import get_logger
from .validator_font import check_font_rules
from .validator_paragraph import check_paragraph_rules
from .validator_margins import check_margins
from .helpers import find_analysis_start_index
from .template_validator import normalize_template_filters
from .listing_skipper import should_skip_due_to_listing

logger = get_logger("utils.document_analyzer")

def check_document_format(doc_path: str, raw_template: dict) -> list[dict]:
    logger.info(f"[START] Анализ документа: {doc_path}")
    errors = []

    try:
        doc = Document(doc_path)
    except Exception as e:
        logger.error(f"[DOCX ERROR] {e}")
        return [{"paragraph_index": 0, "error": "Ошибка открытия документа"}]

    filters = normalize_template_filters(raw_template)
    start_idx = find_analysis_start_index(doc.paragraphs, filters.get("start_after_heading", ""))
    logger.info(f"[ANALYZE FROM] Параграф: {start_idx}")

    base_rules = filters.get("styles", {}).get("Normal", {})

    skip_until_next_heading = False

    for idx, para in enumerate(doc.paragraphs[start_idx:], start=start_idx + 1):
        if skip_until_next_heading:
            if para.style and para.style.name.lower().startswith("heading"):
                skip_until_next_heading = False
            else:
                continue

        if para.style and para.style.name.lower().startswith("heading"):
            if should_skip_due_to_listing(doc.paragraphs, idx - 1):  
                skip_until_next_heading = True
                continue

        errors.extend(check_font_rules(para, idx, base_rules))
        errors.extend(check_paragraph_rules(para, idx, base_rules))

    errors.extend(check_margins(doc, filters.get("margins", {})))

    logger.info(f"[DONE] Найдено ошибок: {len(errors)}")
    return errors
