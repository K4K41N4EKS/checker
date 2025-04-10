from docx.shared import Pt
import logging

logger = logging.getLogger(__name__)

SUPPORTED_PARAMS = {
    "font_name", "font_size", "alignment", "line_spacing",
    "first_line_indent", "bold", "italic", "underline", "all_caps", "font_color_rgb"
}

def normalize_template_filters(raw: dict) -> dict:
    result = {"styles": {}, "margins": {}, "start_after_heading": ""}

    if not isinstance(raw, dict):
        logger.warning("Получен некорректный шаблон: не словарь")
        return result

    # margins
    if "margins" in raw and isinstance(raw["margins"], dict):
        result["margins"] = {
            k: float(v) for k, v in raw["margins"].items()
            if isinstance(v, (int, float)) and k in {"top", "bottom", "left", "right"}
        }

    # heading
    result["start_after_heading"] = str(raw.get("start_after_heading", "")).strip()

    # styles
    raw_styles = raw.get("styles", {})
    for style, params in raw_styles.items():
        if not isinstance(params, dict):
            continue
        validated = {}
        for key, val in params.items():
            if key not in SUPPORTED_PARAMS:
                continue
            if key in {"font_name"}:
                validated[key] = val if isinstance(val, list) else [str(val)]
            elif key in {"font_size"}:
                validated[key] = [float(v) for v in val] if isinstance(val, list) else [float(val)]
            elif key in {"line_spacing", "first_line_indent"}:
                validated[key] = float(val)
            elif key in {"bold", "italic", "underline", "all_caps"}:
                validated[key] = bool(val)
            elif key == "alignment":
                validated[key] = str(val).upper()
            elif key == "font_color_rgb":
                validated[key] = str(val).lower()
        if validated:
            result["styles"][style] = validated

    return result
