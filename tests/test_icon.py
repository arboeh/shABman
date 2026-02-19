# tests\test_icon.py

"""Test shABman icon."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.shabman.helpers import async_register_icon


@pytest.fixture
def mock_hass():
    hass = MagicMock()
    hass.http = None
    hass.config.path.return_value = "/config"
    return hass


@pytest.mark.asyncio
async def test_icon_skip(mock_hass):
    """Skip wenn hass.http=None."""
    result = await async_register_icon(mock_hass)
    assert not result


@pytest.mark.asyncio
async def test_icon_old_api(mock_hass):
    """Alte API (deine HA 2026)."""
    mock_hass.http = MagicMock(register_static_path=MagicMock())

    with patch("custom_components.shabman.helpers.Path.exists", return_value=True):
        result = await async_register_icon(mock_hass)
        assert result
