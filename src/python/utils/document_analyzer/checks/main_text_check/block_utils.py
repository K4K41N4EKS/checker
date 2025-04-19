def is_heading(paragraph):
    return paragraph.style.name.lower().startswith("heading")

def is_picture_caption(paragraph):
    return paragraph.text.strip().lower().startswith("рисунок")

def is_table_caption(paragraph):
    return paragraph.text.strip().lower().startswith("таблица")
