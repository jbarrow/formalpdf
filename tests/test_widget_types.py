import pytest
from pathlib import Path

import pypdfium2.raw as pdfium_c
from formalpdf import Document

# Directory containing PDF test fixtures
DATA_DIR = Path(__file__).parent / "data"

@pytest.mark.parametrize("filename, expected_type, expected_str", [
    ("text_inputs.pdf", pdfium_c.FPDF_FORMFIELD_TEXTFIELD, "Text"),
    ("signature.pdf", pdfium_c.FPDF_FORMFIELD_SIGNATURE, "Signature"),
    ("radio.pdf", pdfium_c.FPDF_FORMFIELD_RADIOBUTTON, "RadioButton"),
    ("radio_single_other.pdf", pdfium_c.FPDF_FORMFIELD_RADIOBUTTON, "RadioButton"),
    ("checkbox.pdf", pdfium_c.FPDF_FORMFIELD_CHECKBOX, "CheckBox"),
    ("checkbox_single.pdf", pdfium_c.FPDF_FORMFIELD_CHECKBOX, "CheckBox"),
    ("checkbox_multiple_other.pdf", pdfium_c.FPDF_FORMFIELD_CHECKBOX, "CheckBox"),
    ("checkbox_bordered.pdf", pdfium_c.FPDF_FORMFIELD_CHECKBOX, "CheckBox"),
    ("checkbox_double.pdf", pdfium_c.FPDF_FORMFIELD_CHECKBOX, "CheckBox"),
])
def test_widget_field_types(filename, expected_type, expected_str):
    """
    Ensure that widgets in various PDF fixtures report the correct field type and string.
    """
    pdf_path = DATA_DIR / filename
    # Load the document and collect all widgets across pages
    doc = Document(str(pdf_path))
    widgets = []
    for page in doc:
        widgets.extend(page.widgets())
    # There should be at least one widget in these fixtures
    assert widgets, f"No widgets found in {filename}"
    # Check each widget's type
    for widget in widgets:
        assert widget.field_type == expected_type, (
            f"{filename}: Expected field_type {expected_type}, got {widget.field_type}"
        )
        assert widget.field_type_string == expected_str, (
            f"{filename}: Expected field_type_string '{expected_str}', got '{widget.field_type_string}'"
        )