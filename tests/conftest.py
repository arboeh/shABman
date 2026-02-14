"""Fixtures for shABman tests."""
import pytest
from unittest.mock import patch, MagicMock
from homeassistant.core import HomeAssistant

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Enable custom integration loading."""
    yield


@pytest.fixture
def mock_device_info():
    """Mock Shelly device info response."""
    return {
        "name": "Shelly Plus 1PM Test",
        "id": "shellypluspm-test123",
        "model": "SNSW-001P16EU",
        "gen": 2,
        "fw_id": "20230913-114336/v1.14.0-gcb84623",
        "ver": "1.14.0",
        "app": "Plus1PM",
    }


@pytest.fixture
def mock_scripts_list():
    """Mock Script.List response."""
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
                "name": "Energy_Monitor",
                "enable": False,
                "running": False,
            },
        ]
    }


@pytest.fixture
async def mock_aiohttp_client():
    """Mock aiohttp ClientSession."""
    with patch("aiohttp.ClientSession") as mock_session:
        yield mock_session
