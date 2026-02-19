# tests\test_icon.py

"""Test shABman icon."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.shabman.helpers import register_icon


@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.http = None
    hass.config.path.return_value = "/config"
    return hass


def test_icon_skipped(mock_hass):  # ← Kein async!
    result = register_icon(mock_hass)
    assert not result


def test_icon_success(mock_hass):
    mock_hass.http = MagicMock()
    mock_hass.http.register_static_path = MagicMock()

    with patch("custom_components.shabman.helpers.Path.exists", return_value=True):
        result = register_icon(mock_hass)
        assert result
        mock_hass.http.register_static_path.assert_called_once()


def test_icon_missing(mock_hass):
    mock_hass.http = MagicMock()
    with patch("custom_components.shabman.helpers.Path.exists", return_value=False):
        result = register_icon(mock_hass)
        assert not result
