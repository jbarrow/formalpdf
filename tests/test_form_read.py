from __future__ import annotations

from pathlib import Path
import pytest

from formalpdf import Document


DATA_DIR = Path(__file__).parent / "data"


def _all_pdf_paths() -> list[Path]:
    return sorted(DATA_DIR.glob("*.pdf"))


@pytest.mark.parametrize("pdf_path", _all_pdf_paths(), ids=lambda p: p.name)
def test_open_and_list_widgets(pdf_path: Path):
    doc = Document(str(pdf_path))

    # ensure we can iterate pages and collect widgets without errors
    total = 0
    for page in doc:
        widgets = page.widgets()
        assert isinstance(widgets, list)
        total += len(widgets)

    # sanity check: files named no_widgets should actually have none
    if pdf_path.stem == "no_widgets":
        assert total == 0
    else:
        # For now, just ensure non-negative (basic smoke test)
        assert total >= 0
