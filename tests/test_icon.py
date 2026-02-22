# tests\test_icon.py

"""Test shABman icon."""

from unittest.mock import MagicMock, patch

import pytest

from custom_components.shabman.helpers import HAS_NEW_API, async_register_icon


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


@pytest.mark.skipif(HAS_NEW_API, reason="Tests new StaticPathConfig API only (HA 2026.2+)")
@pytest.mark.asyncio
async def test_icon_old_api(mock_hass):
    """Deprecated API (vor HA 2026.2)."""
    mock_hass.http = MagicMock(register_static_path=MagicMock())

    with patch("custom_components.shabman.helpers.Path.exists", return_value=True):
        result = await async_register_icon(mock_hass)
        assert result
