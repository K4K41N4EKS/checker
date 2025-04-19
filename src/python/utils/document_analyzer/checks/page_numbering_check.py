from docx import Document
from lxml import etree

def check_page_numbering(path: str) -> list[dict]:
    doc = Document(path)
    errors = []

    has_numbering = False
    has_different_first_page = False

    WORD_NAMESPACE = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

    for section in doc.sections:
        if section.different_first_page_header_footer:
            has_different_first_page = True

        for footer in [section.footer, section.first_page_footer, section.even_page_footer]:
            xml = footer._element.xml

            # Простой поиск: <w:fldSimple w:instr=" PAGE ">
            if 'w:fldSimple' in xml and 'PAGE' in xml:
                has_numbering = True
                break

            # Поиск через lxml xpath без аргумента namespaces
            tree = etree.fromstring(xml.encode('utf-8'))
            instr_texts = tree.findall(".//{%s}instrText" % WORD_NAMESPACE)
            if any("PAGE" in instr.text for instr in instr_texts if instr.text):
                has_numbering = True
                break

    if not has_numbering:
        errors.append({
            "paragraph_index": 0,
            "error": "Отсутствует нумерация страниц в колонтитулах"
        })

    if not has_different_first_page:
        errors.append({
            "paragraph_index": 0,
            "error": "Не установлен особый колонтитул для первой страницы"
        })

    return errors
