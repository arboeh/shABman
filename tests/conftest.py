# tests/conftest.py

"""Fixtures for shABman tests."""

import os
from unittest.mock import Mock

import pytest
import pytest_socket

# Setze Timezone VOR allen Imports
os.environ["TZ"] = "UTC"

pytest_socket.disable_socket = Mock()
pytest_socket.socket_allow_hosts = Mock()

# Jetzt erst pytest_homeassistant_custom_component laden
pytest_plugins = ["pytest_homeassistant_custom_component"]


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
