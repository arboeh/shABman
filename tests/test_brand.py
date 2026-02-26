# tests/test_brand.py

"""Test shABman brand assets."""

from pathlib import Path

BRAND_DIR = Path("custom_components/shabman/brand")


def test_brand_icon_exists():
    """brand/icon.png muss vorhanden sein."""
    assert (BRAND_DIR / "icon.png").exists(), "brand/icon.png fehlt"


# def test_brand_logo_exists():
#     """brand/logo.png muss vorhanden sein."""
#     assert (BRAND_DIR / "logo.png").exists(), "brand/logo.png fehlt"
