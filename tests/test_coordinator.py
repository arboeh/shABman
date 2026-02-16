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


# ===== Coordinator Tests =====


async def test_coordinator_update(hass: HomeAssistant, mock_config_entry, mock_scripts_list):
    """Test coordinator update."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    with patch.object(coordinator, "list_scripts", return_value=mock_scripts_list["scripts"]):
        await coordinator.async_config_entry_first_refresh()

        assert "scripts" in coordinator.data
        assert len(coordinator.data["scripts"]) == 2


async def test_coordinator_update_failed(hass: HomeAssistant, mock_config_entry):
    """Test coordinator update failure."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    with patch.object(coordinator, "list_scripts", side_effect=Exception("Connection error")):
        with pytest.raises(UpdateFailed):
            await coordinator._async_update_data()


# ===== HTTP Request Tests =====


async def test_list_scripts_success(hass: HomeAssistant, mock_config_entry):
    """Test listing scripts successfully."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    mock_scripts = [
        {"id": 1, "name": "test1", "enable": True, "running": False},
        {"id": 2, "name": "test2", "enable": False, "running": False},
    ]

    with patch.object(coordinator, "list_scripts", return_value=mock_scripts):
        scripts = await coordinator.list_scripts()

        assert len(scripts) == 2
        assert scripts[0]["name"] == "test1"
        assert scripts[1]["name"] == "test2"


async def test_get_script_code_success(hass: HomeAssistant, mock_config_entry):
    """Test getting script code successfully."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    mock_code = "let x = 1;"

    with patch.object(coordinator, "get_script_code", return_value=mock_code):
        code = await coordinator.get_script_code(1)

        assert code == "let x = 1;"


async def test_start_script(hass: HomeAssistant, mock_config_entry):
    """Test starting a script."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    with patch.object(coordinator, "start_script", return_value=True):
        result = await coordinator.start_script(1)
        assert result is True


async def test_stop_script(hass: HomeAssistant, mock_config_entry):
    """Test stopping a script."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    with patch.object(coordinator, "stop_script", return_value=True):
        result = await coordinator.stop_script(1)
        assert result is True


async def test_upload_script(hass: HomeAssistant, mock_config_entry):
    """Test script upload."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    with patch.object(coordinator, "upload_script", return_value=True):
        result = await coordinator.upload_script("test_script", "console.log('test');")
        assert result is True


async def test_delete_script(hass: HomeAssistant, mock_config_entry):
    """Test script deletion."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    with patch.object(coordinator, "delete_script", return_value=True):
        result = await coordinator.delete_script(1)
        assert result is True


async def test_set_script_config(hass: HomeAssistant, mock_config_entry):
    """Test setting script configuration (autostart)."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)

    with patch.object(coordinator, "set_script_config", return_value=True):
        result = await coordinator.set_script_config(1, enabled=True)
        assert result is True
