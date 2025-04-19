import re

def is_static_header(text: str) -> bool:
    return text.lower() in {"введение", "заключение", "список использованных источников"}

def is_main_header_lvl_1(text: str) -> bool:
    return bool(re.match(r"^\d+ [А-ЯЁ ]+$", text))

def is_main_header_lvl_2(text: str) -> bool:
    return bool(re.match(r"^\d+\.\d+ .+", text))

def is_main_header_lvl_3(text: str) -> bool:
    return bool(re.match(r"^\d+\.\d+\.\d+ .+", text))
