def should_skip_due_to_listing(paragraphs, idx: int) -> bool:
    """
    Если параграф — заголовок с "Приложение", и в следующих 5 абзацах
    встречается слово "листинг", значит, нужно пропустить блок до следующего заголовка.
    """
    current_text = paragraphs[idx].text.strip().lower()
    if "приложение" not in current_text:
        return False

    for offset in range(1, 6):
        next_idx = idx + offset
        if next_idx < len(paragraphs):
            if "листинг" in paragraphs[next_idx].text.strip().lower():
                return True
    return False