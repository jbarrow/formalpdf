from __future__ import annotations

import shutil
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def output_dir() -> Path:
    """Create a temporary tests/output directory for generated PDFs and clean it up after the session."""
    base = Path(__file__).parent / "output"
    # Ensure a clean directory for this test session
    if base.exists():
        shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True, exist_ok=True)
    try:
        yield base
    finally:
        # Remove the directory and all its contents
        shutil.rmtree(base, ignore_errors=True)

