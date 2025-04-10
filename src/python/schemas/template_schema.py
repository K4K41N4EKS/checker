from typing import List, Literal, Optional, Annotated
from pydantic import BaseModel, ConfigDict, Field, field_validator, StringConstraints
from decimal import Decimal

class TemplateBase(BaseModel):
    name: str
    filters: dict

class TemplateCreate(TemplateBase):
    pass

class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    filters: Optional[dict] = None

class TemplateResponse(TemplateBase):
    id: str
    user_id: str

    class Config:
        model_config = {
            "from_attributes": True
        }

# Кастомные типы с ограничениями
FontName = Annotated[
    str,
    StringConstraints(pattern="^(Times New Roman|Arial|Calibri)$")
]

FontSize = Annotated[int, Field(ge=12, le=14)]
LineSpacing = Annotated[float, Field(ge=1.0, le=2.0, multiple_of=0.5)]
Indent = Annotated[float, Field(ge=0.0, le=1.5)]
MarginValue = Annotated[float, Field(ge=1.0, le=4.0)]

# Дополнительные модели для валидации filters
class MarginModel(BaseModel):
    top: MarginValue
    bottom: MarginValue
    left: Annotated[float, Field(ge=1.5, le=4.0)]
    right: Annotated[float, Field(ge=1.0, le=2.0)]

    @field_validator('*', mode='before')
    @classmethod
    def round_margins(cls, v: float) -> float:
        return round(float(v), 2)

class StyleModel(BaseModel):
    font_name: List[FontName] = Field(..., min_length=1, max_length=3)
    font_size: List[FontSize] = Field(..., min_length=1, max_length=2)
    font_color_rgb: Optional[str] = Field(None, pattern="^[0-9a-fA-F]{6}$")
    bold: bool = False
    italic: bool = False
    underline: bool = False
    all_caps: bool = False
    alignment: Optional[Literal["LEFT", "RIGHT", "CENTER", "JUSTIFY"]] = None
    line_spacing: Optional[LineSpacing] = None
    first_line_indent: Optional[Indent] = None

class FiltersModel(BaseModel):
    start_after_heading: str
    margins: MarginModel
    styles: dict[str, StyleModel]
    heading_levels: Optional[Literal[1, 2, 3]] = None
    numbering_type: Optional[Literal["sectional", "continuous"]] = None
    page_number_format: Optional[
        Literal["bottom_center", "bottom_right", "top_right"]
    ] = None
    toc_format: Optional[
        Literal["with_dots", "without_dots", "without_numbers"]
    ] = None

    @field_validator('styles')
    @classmethod
    def validate_headings(cls, v: dict) -> dict:
        if "Heading1" in v:
            style = v["Heading1"]
            if not style.all_caps or not style.bold:
                raise ValueError("Heading1 must be ALL_CAPS and BOLD")
        if "Heading2" in v:
            style = v["Heading2"]
            if style.all_caps or not style.bold:
                raise ValueError("Heading2 must be lowercase and BOLD")
        return v
    
# Расширенные модели для валидации filters
class ValidatedTemplateResponse(TemplateResponse):
    model_config = ConfigDict(from_attributes=True)
    
    @field_validator('filters')
    @classmethod
    def validate_filters(cls, v: dict) -> dict:
        return FiltersModel(**v).model_dump()

class ValidatedTemplateCreate(TemplateCreate):
    @field_validator('filters')
    @classmethod
    def validate_filters(cls, v: dict) -> dict:
        return FiltersModel(**v).model_dump()
    