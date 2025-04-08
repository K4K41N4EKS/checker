def is_paragraph_in_table(para) -> bool:
    return bool(para._element.xpath('ancestor::w:tbl'))

def find_analysis_start_index(paragraphs, marker: str) -> int:
    marker = marker.strip().lower()
    for idx, para in enumerate(paragraphs):
        if marker in para.text.strip().lower():
            return idx + 1
    return 0

