def parse_template(raw_template: dict) -> dict:
    return {k.strip(): v for k, v in raw_template.items()}
