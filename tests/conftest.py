# tests/conftest.py

"""Fixtures for shABman tests."""

import uuid
from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from custom_components.shabman import async_setup_entry, async_unload_entry
from custom_components.shabman.const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN


# KRITISCH: Disable pytest-socket BEFORE any fixtures run
def pytest_configure(config):
    """Pytest configuration hook - disable socket blocking."""
    import sys

    if "pytest_socket" in sys.modules:
        import pytest_socket

        # Monkey-patch to disable socket blocking
        pytest_socket.socket_disabled = False
        pytest_socket.disable_socket = lambda *args, **kwargs: None
        pytest_socket.enable_socket = lambda *args, **kwargs: None


# Auto-enable custom integrations for Home Assistant
@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Automatically enable custom integrations."""
    yield


@pytest.fixture
def mock_device_info():
    """Mock device info response."""
    return {
        "id": "shellypluspm-test123",
        "mac": "AA:BB:CC:DD:EE:FF",
        "model": "SNSW-001P16EU",
        "gen": 2,
        "fw_id": "20230913-114008/v1.14.0-gcb84623",
        "ver": "1.14.0",
        "app": "Plus1PM",
        "name": "Shelly Plus 1PM Test",
    }


@pytest.fixture
def mock_scripts_list():
    """Mock scripts list response."""
    return {
        "scripts": [
            {
                "id": 1,
                "name": "BLU_Gateway",
                "enable": True,
                "running": True,
            },
            {
                "id": 2,
                "name": "test_script",
                "enable": False,
                "running": False,
            },
        ]
    }


@pytest.fixture
def mock_script_code():
    """Mock script code response."""
    return {
        "data": "console.log('Hello from script');\n// More script code here",
    }


@pytest.fixture
async def setup_integration(hass: HomeAssistant, mock_scripts_list):
    """Set up the shabman integration."""
    # Create unique ID for each test
    unique_id = str(uuid.uuid4())

    entry = ConfigEntry(
        version=1,
        minor_version=0,
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": f"test_{unique_id}",
        },
        source="user",
        unique_id=unique_id,
    )

    # Register entry in hass
    hass.config_entries._entries[entry.entry_id] = entry

    # Mock websocket listener to prevent it from actually running
    async def mock_websocket_listener():
        """Mock websocket listener that does nothing."""
        pass

    # Mock coordinator methods with proper return data
    with patch(
        "custom_components.shabman.coordinator.ShABmanCoordinator.list_scripts",
        return_value=mock_scripts_list["scripts"],
    ), patch(
        "custom_components.shabman.coordinator.ShABmanCoordinator._async_update_data",
        return_value={
            "scripts": mock_scripts_list["scripts"],
            "device_type": "SNSW-001X16EU",
            "running_count": 1,
            "enabled_count": 1,
        },
    ), patch(
        "custom_components.shabman.coordinator.ShABmanCoordinator._websocket_listener",
        side_effect=mock_websocket_listener,
    ):
        # Setup the integration
        result = await async_setup_entry(hass, entry)
        assert result is True
        await hass.async_block_till_done()

    # WICHTIG: yield MUSS hier sein!
    yield entry

    # Cleanup
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        coordinator = hass.data[DOMAIN][entry.entry_id]
        if hasattr(coordinator, "_ws_task") and coordinator._ws_task:
            coordinator._ws_task.cancel()
            try:
                await coordinator._ws_task
            except Exception:
                pass

    try:
        await async_unload_entry(hass, entry)
        await hass.async_block_till_done()
    except Exception:
        pass
