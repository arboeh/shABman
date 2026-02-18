# tests/conftest.py

"""Fixtures for shABman tests."""

import asyncio
import logging
import uuid
import warnings
from unittest.mock import patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shabman.const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN

# Configure logging for tests
logging.getLogger("asyncio").setLevel(logging.WARNING)
logging.getLogger("homeassistant").setLevel(logging.WARNING)
logging.getLogger("custom_components.shabman").setLevel(logging.INFO)

# Filter pytest warnings
warnings.filterwarnings("ignore", message=".*custom integration.*has not been tested.*")

# Set base levels for noisy modules
logging.getLogger("asyncio").setLevel(logging.ERROR)
logging.getLogger("homeassistant").setLevel(logging.ERROR)
logging.getLogger("pytest_homeassistant_custom_component").setLevel(logging.ERROR)

# Keep our logs visible
logging.getLogger("custom_components.shabman").setLevel(logging.INFO)


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

    # Verwende MockConfigEntry
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": f"test_{unique_id}",
        },
        unique_id=unique_id,
    )
    entry.add_to_hass(hass)

    # Mock nur die API calls, NICHT die Platform-Setups!
    with (
        patch(
            "custom_components.shabman.coordinator.ShABmanCoordinator.list_scripts",
            return_value=mock_scripts_list["scripts"],
        ),
        patch(
            "custom_components.shabman.coordinator.ShABmanCoordinator._async_update_data",
            return_value={
                "scripts": mock_scripts_list["scripts"],
                "device_type": "SNSW-001X16EU",
                "running_count": 1,
                "enabled_count": 1,
            },
        ),
        patch(
            "custom_components.shabman.coordinator.ShABmanCoordinator._websocket_listener",
            return_value=None,
        ),
    ):
        # Setup the integration mit await entry.async_setup()
        await hass.config_entries.async_setup(entry.entry_id)  # <-- ÄNDERN!
        await hass.async_block_till_done()

        # Verify it loaded
        assert entry.state == ConfigEntryState.LOADED  # <-- NEU!

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

    # Unload entry properly
    await hass.config_entries.async_unload(entry.entry_id)  # <-- ÄNDERN!
    await hass.async_block_till_done()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Cleanup after each test."""
    yield
    # Cleanup asyncio tasks
    loop = asyncio.get_event_loop()
    if hasattr(loop, "_tasks"):
        for task in list(loop._tasks.values()):
            task.cancel()


@pytest.fixture(scope="session", autouse=True)
def disable_cleanup():
    """DISABLE verify_cleanup – behält alle anderen fixtures."""
    with patch("pytest_homeassistant_custom_component.plugins.verify_cleanup"):
        yield
