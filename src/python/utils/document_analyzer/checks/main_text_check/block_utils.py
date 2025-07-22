import re

def is_heading(paragraph) -> bool:
    """Вернёт True, если абзац является заголовком (по стилю или по содержимому)."""
    text = paragraph.text.strip()
    if not text:
        return False
    # Стиль Word (например, Heading 1/2/3)
    if paragraph.style and paragraph.style.name and paragraph.style.name.lower().startswith("heading"):
        return True
    # Статические заголовки
    low = text.lower()
    if low in {"введение", "заключение", "список использованных источников", "приложение", "приложения"}:
        return True
    # Нумерованные заголовки
    if re.match(r'^\d+ ', text) or re.match(r'^\d+\.\d+ ', text) or re.match(r'^\d+\.\d+\.\d+ ', text):
        return True
    return False


def is_picture_caption(paragraph):
    return paragraph.text.strip().lower().startswith("рисунок")

def is_table_caption(paragraph):
    return paragraph.text.strip().lower().startswith("таблица")
