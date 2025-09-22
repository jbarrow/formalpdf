from pathlib import Path

import pytest

import formalpdf


DATA_DIR = Path(__file__).parent / "data"


def _pdf(path: str) -> Path:
    return DATA_DIR / path


def _count_widgets(doc: formalpdf.Document) -> list[int]:
    return [len(page.widgets()) for page in doc]


def test_merge_complete_document(output_dir: Path):
    dest = formalpdf.open(_pdf("text_inputs.pdf"))
    src = formalpdf.open(_pdf("checkbox.pdf"))

    before = len(dest)
    added = len(src)

    dest.insert_pdf(src)

    assert len(dest) == before + added

    out = output_dir / "merge_complete.pdf"
    dest.save(str(out))
    assert out.exists() and out.stat().st_size > 0


def test_merge_range(output_dir: Path):
    dest = formalpdf.open(_pdf("text_inputs.pdf"))
    src = formalpdf.open(_pdf("checkbox.pdf"))

    before = len(dest)
    # take at most first 2 pages from src
    from_page = 0
    to_page = min(2, len(src))
    expected_added = max(0, to_page - from_page)

    dest.insert_pdf(src, from_page=from_page, to_page=to_page)
    assert len(dest) == before + expected_added

    out = output_dir / "merge_range.pdf"
    dest.save(str(out))
    assert out.exists() and out.stat().st_size > 0


def test_merge_at_index(output_dir: Path):
    dest = formalpdf.open(_pdf("text_inputs.pdf"))
    src = formalpdf.open(_pdf("checkbox.pdf"))

    # capture widget counts of src to validate placement
    src_widget_counts = _count_widgets(src)
    assert src_widget_counts, "Source document unexpectedly has zero pages"

    # insert at the beginning
    dest.insert_pdf(src, index=0)

    # After insertion, the first len(src) pages should correspond to src pages
    for i, expected in enumerate(src_widget_counts):
        assert len(dest[i].widgets()) == expected

    out = output_dir / "merge_at_index.pdf"
    dest.save(str(out))
    assert out.exists() and out.stat().st_size > 0


def test_widgets_maintained_during_merge(output_dir: Path):
    dest = formalpdf.open(_pdf("text_inputs.pdf"))
    src = formalpdf.open(_pdf("checkbox.pdf"))

    src_widget_counts = _count_widgets(src)
    # Sanity: ensure src actually has widgets to make this meaningful
    assert any(c > 0 for c in src_widget_counts)

    dest.insert_pdf(src, index=0)

    # Compare per-page widget counts for the inserted range
    for i, expected in enumerate(src_widget_counts):
        assert len(dest[i].widgets()) == expected

    out = output_dir / "merge_widgets_preserved.pdf"
    dest.save(str(out))
    assert out.exists() and out.stat().st_size > 0


def test_merge_document_with_itself(output_dir: Path):
    # Open the same file twice to simulate merging a document with itself
    original = formalpdf.open(_pdf("text_inputs.pdf"))
    dest = formalpdf.open(_pdf("text_inputs.pdf"))

    before = len(dest)
    added = len(original)

    dest.insert_pdf(original)
    assert len(dest) == before + added

    out = output_dir / "merge_self.pdf"
    dest.save(str(out))
    assert out.exists() and out.stat().st_size > 0
