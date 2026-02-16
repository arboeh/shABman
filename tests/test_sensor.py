# tests\test_sensor.py

"""Test the shABman sensor entities."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er

from custom_components.shabman.const import DOMAIN


async def test_sensor_script_count_created(hass: HomeAssistant, setup_integration):
    """Test that script count sensor is created."""
    entry = setup_integration
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Get entity_id from unique_id
    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{coordinator.device_ip}_script_count")

    assert entity_id is not None
    assert entity_id == "sensor.shelly_script_manager_script_count"


async def test_sensor_running_scripts_created(hass: HomeAssistant, setup_integration):
    """Test that running scripts sensor is created."""
    entry = setup_integration
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entity_registry = er.async_get(hass)
    entity_id = entity_registry.async_get_entity_id("sensor", DOMAIN, f"{coordinator.device_ip}_running_scripts")

    assert entity_id is not None
    assert entity_id == "sensor.shelly_script_manager_running_scripts"


async def test_sensor_script_count_value(hass: HomeAssistant, setup_integration):
    """Test script count sensor value."""
    state = hass.states.get("sensor.shelly_script_manager_script_count")
    assert state is not None
    assert state.state == "2"  # Two scripts in mock_scripts_list


async def test_sensor_running_scripts_value(hass: HomeAssistant, setup_integration):
    """Test running scripts sensor value."""
    state = hass.states.get("sensor.shelly_script_manager_running_scripts")
    assert state is not None
    assert state.state == "1"  # One running script in mock_scripts_list


async def test_sensor_running_scripts_attributes(hass: HomeAssistant, setup_integration):
    """Test running scripts sensor attributes."""
    state = hass.states.get("sensor.shelly_script_manager_running_scripts")
    assert state is not None
    assert "running_script_names" in state.attributes
    assert "BLU_Gateway" in state.attributes["running_script_names"]
