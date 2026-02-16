# custom_components\shabman\sensor.py

"""Sensor platform for shABman."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import ShABmanCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up shABman sensors."""
    coordinator: ShABmanCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create sensor entities
    entities = [
        ScriptCountSensor(coordinator),
        RunningScriptsSensor(coordinator),
    ]

    async_add_entities(entities)


class ScriptCountSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total script count."""

    def __init__(self, coordinator: ShABmanCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{coordinator.device_ip}_script_count"
        self._attr_name = "Script Count"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:script-text"

        # Device info for grouping
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_ip)},
            "name": "Shelly Script Manager",
            "manufacturer": "Shelly",
            "model": coordinator.device_type,
            "sw_version": "1.0",
        }

    @property
    def native_value(self) -> int:
        """Return the state."""
        scripts = self.coordinator.data.get("scripts", [])
        return len(scripts)


class RunningScriptsSensor(CoordinatorEntity, SensorEntity):
    """Sensor for running scripts count."""

    def __init__(self, coordinator: ShABmanCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        self._attr_unique_id = f"{coordinator.device_ip}_running_scripts"
        self._attr_name = "Running Scripts"
        self._attr_has_entity_name = True
        self._attr_icon = "mdi:play-circle"

        # Device info for grouping
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_ip)},
            "name": "Shelly Script Manager",
            "manufacturer": "Shelly",
            "model": coordinator.device_type,
            "sw_version": "1.0",
        }

    @property
    def native_value(self) -> int:
        """Return the state."""
        return self.coordinator.data.get("running_count", 0)

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        scripts = self.coordinator.data.get("scripts", [])
        running_scripts = [s["name"] for s in scripts if s.get("running")]
        return {"running_script_names": running_scripts}
