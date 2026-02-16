# tests/test_coordinator.py

"""Test the shABman coordinator."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shabman.const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN
from custom_components.shabman.coordinator import ShABmanCoordinator


@pytest.fixture
def mock_config_entry(hass):
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        unique_id="test123",
    )
    entry.add_to_hass(hass)  # <-- WICHTIG!
    return entry


@pytest.fixture
def mock_coordinator(hass, mock_config_entry):
    """Create a coordinator with mocked websocket."""
    with patch("custom_components.shabman.coordinator.ShABmanCoordinator._websocket_listener"):
        coordinator = ShABmanCoordinator(hass, mock_config_entry)
        yield coordinator

        # Cleanup
        if hasattr(coordinator, "_ws_task") and coordinator._ws_task:
            coordinator._ws_task.cancel()


# ===== Coordinator Tests =====


async def test_coordinator_update(hass: HomeAssistant, mock_coordinator, mock_scripts_list):
    """Test coordinator update."""
    with patch.object(mock_coordinator, "list_scripts", return_value=mock_scripts_list["scripts"]):
        await mock_coordinator.async_refresh()

        assert "scripts" in mock_coordinator.data
        assert len(mock_coordinator.data["scripts"]) == 2


async def test_coordinator_update_failed(hass: HomeAssistant, mock_coordinator):
    """Test coordinator update failure."""
    with patch.object(mock_coordinator, "list_scripts", side_effect=Exception("Connection error")):
        with pytest.raises(UpdateFailed):
            await mock_coordinator._async_update_data()


# ===== HTTP Request Tests =====


async def test_list_scripts_success(hass: HomeAssistant, mock_coordinator):
    """Test listing scripts successfully."""
    mock_scripts = [
        {"id": 1, "name": "test1", "enable": True, "running": False},
        {"id": 2, "name": "test2", "enable": False, "running": False},
    ]

    with patch.object(mock_coordinator, "list_scripts", return_value=mock_scripts):
        scripts = await mock_coordinator.list_scripts()

        assert len(scripts) == 2
        assert scripts[0]["name"] == "test1"
        assert scripts[1]["name"] == "test2"


async def test_get_script_code_success(hass: HomeAssistant, mock_coordinator):
    """Test getting script code successfully."""
    mock_code = "let x = 1;"

    with patch.object(mock_coordinator, "get_script_code", return_value=mock_code):
        code = await mock_coordinator.get_script_code(1)

        assert code == "let x = 1;"


async def test_start_script(hass: HomeAssistant, mock_coordinator):
    """Test starting a script."""
    with patch.object(mock_coordinator, "start_script", return_value=True):
        result = await mock_coordinator.start_script(1)
        assert result is True


async def test_stop_script(hass: HomeAssistant, mock_coordinator):
    """Test stopping a script."""
    with patch.object(mock_coordinator, "stop_script", return_value=True):
        result = await mock_coordinator.stop_script(1)
        assert result is True


async def test_upload_script(hass: HomeAssistant, mock_coordinator):
    """Test script upload."""
    with patch.object(mock_coordinator, "upload_script", return_value=True):
        result = await mock_coordinator.upload_script("test_script", "console.log('test');")
        assert result is True


async def test_delete_script(hass: HomeAssistant, mock_coordinator):
    """Test script deletion."""
    with patch.object(mock_coordinator, "delete_script", return_value=True):
        result = await mock_coordinator.delete_script(1)
        assert result is True


async def test_set_script_config(hass: HomeAssistant, mock_coordinator):
    """Test setting script configuration (autostart)."""
    with patch.object(mock_coordinator, "set_script_config", return_value=True):
        result = await mock_coordinator.set_script_config(1, enabled=True)
        assert result is True
