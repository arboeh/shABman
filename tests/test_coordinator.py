# tests/test_coordinator.py

"""Test the shABman coordinator."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed

from custom_components.shabman.const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN
from custom_components.shabman.coordinator import ShABmanCoordinator

# ===== Coordinator Tests =====


async def test_coordinator_update(hass: HomeAssistant, mock_scripts_list):
    """Test coordinator update."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    with patch.object(coordinator, "list_scripts", return_value=mock_scripts_list["scripts"]):
        await coordinator.async_config_entry_first_refresh()

        assert "scripts" in coordinator.data
        assert len(coordinator.data["scripts"]) == 2


async def test_coordinator_update_failed(hass: HomeAssistant):
    """Test coordinator update failure."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    with patch.object(coordinator, "list_scripts", side_effect=Exception("Connection error")):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


# ===== HTTP Request Tests =====


async def test_list_scripts_success(hass: HomeAssistant):
    """Test listing scripts successfully."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(
        return_value={
            "scripts": [
                {"id": 1, "name": "test1", "enable": True},
                {"id": 2, "name": "test2", "enable": False},
            ]
        }
    )

    # Mock session.get() context manager
    mock_get_ctx = MagicMock()
    mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

    # Mock session context manager
    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_get_ctx)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Patch ClientSession
    with patch("aiohttp.ClientSession", return_value=mock_session):
        scripts = await coordinator.list_scripts()

        assert len(scripts) == 2
        assert scripts[0]["name"] == "test1"
        assert scripts[1]["name"] == "test2"


async def test_get_script_code_success(hass: HomeAssistant):
    """Test getting script code successfully."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"data": "let x = 1;"})

    # Mock session.get() context manager
    mock_get_ctx = MagicMock()
    mock_get_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_get_ctx.__aexit__ = AsyncMock(return_value=None)

    # Mock session context manager
    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=mock_get_ctx)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Patch ClientSession
    with patch("aiohttp.ClientSession", return_value=mock_session):
        code = await coordinator.get_script_code(1)

        assert code == "let x = 1;"


async def test_start_script(hass: HomeAssistant):
    """Test starting a script."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"was_running": False})

    # Mock session.post() context manager
    mock_post_ctx = MagicMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=None)

    # Mock session context manager
    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_post_ctx)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Patch ClientSession
    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await coordinator.start_script(1)
        assert result is True


async def test_stop_script(hass: HomeAssistant):
    """Test stopping a script."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"was_running": True})

    # Mock session.post() context manager
    mock_post_ctx = MagicMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=None)

    # Mock session context manager
    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_post_ctx)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Patch ClientSession
    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await coordinator.stop_script(1)
        assert result is True


async def test_upload_script(hass: HomeAssistant):
    """Test script upload."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    # Mock create response
    mock_create_response = AsyncMock()
    mock_create_response.status = 200
    mock_create_response.json = AsyncMock(return_value={"id": 5})

    # Mock put code response
    mock_put_response = AsyncMock()
    mock_put_response.status = 200

    # Mock session.post() context managers
    mock_create_ctx = MagicMock()
    mock_create_ctx.__aenter__ = AsyncMock(return_value=mock_create_response)
    mock_create_ctx.__aexit__ = AsyncMock(return_value=None)

    mock_put_ctx = MagicMock()
    mock_put_ctx.__aenter__ = AsyncMock(return_value=mock_put_response)
    mock_put_ctx.__aexit__ = AsyncMock(return_value=None)

    # Mock session context manager
    mock_session = MagicMock()
    mock_session.post = MagicMock(side_effect=[mock_create_ctx, mock_put_ctx])
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Patch ClientSession
    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await coordinator.upload_script("test_script", "console.log('test');")
        assert result is True


async def test_delete_script(hass: HomeAssistant):
    """Test script deletion."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200

    # Mock session.post() context manager
    mock_post_ctx = MagicMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=None)

    # Mock session context manager
    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_post_ctx)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    # Patch ClientSession
    with patch("aiohttp.ClientSession", return_value=mock_session):
        result = await coordinator.delete_script(1)
        assert result is True


async def test_set_script_config(hass: HomeAssistant):
    """Test setting script configuration (autostart)."""
    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        source="user",
        unique_id="test123",
    )

    coordinator = ShABmanCoordinator(hass, entry)

    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200

    mock_post_ctx = MagicMock()
    mock_post_ctx.__aenter__ = AsyncMock(return_value=mock_response)
    mock_post_ctx.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.post = MagicMock(return_value=mock_post_ctx)
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    with patch("aiohttp.ClientSession", return_value=mock_session):
        # FIX: Verwende die richtige Methode aus deinem Code
        result = await coordinator.set_script_config(1, True)  # ← OHNE enable= keyword!
        assert result is True
