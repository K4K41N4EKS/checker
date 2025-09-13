# Error Codes for Document Checker

This document lists machine-readable error codes emitted by the DOCX checker, to help the frontend group and display issues consistently.

Each error has the shape:

- paragraph_index: number (0 for document-level)
- error: human-readable message
- code: one of the codes below
- category: formatting | structure | numbering | references | document
- severity: error | warning | info
- meta: optional object with context (e.g., expected/actual values)

## Formatting

- FONT_NAME_MISMATCH: Wrong font family.
  - meta: { expected: string[] | string, actual: string }
- FONT_SIZE_MISMATCH: Wrong font size.
  - meta: { expected: number, actual: number }
- ALIGNMENT_MISMATCH: Wrong paragraph alignment (left/center/right/justify).
  - meta: { expected: string[] | string, actual: string }
- INDENT_MISMATCH: Wrong first-line/left indent.
  - meta: { expected: number[] | number, actual: number }
- LINE_SPACING_MISMATCH: Wrong line spacing multiplier.
  - meta: { expected: number, actual: number }
- MARGIN_MISMATCH: Page margin does not match template.
  - meta: { field: 'top_margin'|'bottom_margin'|'left_margin'|'right_margin', expected: number, actual: number }

## Structure

- START_INDEX_NOT_FOUND: Could not locate start of main text after configured marker.
  - meta: { start_marker: string }

## Numbering

- PAGE_NUMBERING_MISSING: No PAGE field detected in headers/footers.
- DIFFERENT_FIRST_PAGE_DISABLED: First page not configured as different (cover should be without number).

## References

- REF_SECTION_MISSING: References section heading not found.
- REF_LIST_EMPTY: No numbered items detected in the references list.
- REF_USED_BUT_NOT_LISTED: Citation used in text not present in the references list.
  - meta: { missing: number }
- REF_LISTED_BUT_NOT_USED: Reference listed but not used in text.
  - meta: { unused: number }
- REF_ORDER_NONMONOTONIC: Citations in text are not in non-decreasing order.

## Document

- MARGIN_CONFIG_INVALID: Invalid margin configuration value in the template.

Notes:
- paragraph_index=0 is used for document-level issues (margins, page numbering, etc.).
- The `error` field is for immediate display; rely on `code`+`category` for grouping and localization.

