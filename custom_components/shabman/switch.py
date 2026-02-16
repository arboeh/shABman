# custom_components\shabman\switch.py

"""Switch platform for shABman."""
import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
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
    """Set up shABman switches."""
    coordinator: ShABmanCoordinator = hass.data[DOMAIN][entry.entry_id]

    # Create TWO switch entities for each script
    scripts = coordinator.data.get("scripts", [])
    entities = []

    for script in scripts:
        # 1. Status switch (running/stopped)
        entities.append(ScriptStatusSwitch(coordinator, script))
        # 2. Autostart switch (run on startup)
        entities.append(ScriptAutostartSwitch(coordinator, script))

    async_add_entities(entities)


class ScriptStatusSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control script running status."""

    def __init__(self, coordinator: ShABmanCoordinator, script: dict) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)

        self._script_id = script["id"]
        self._script_name = script["name"]

        # Unique ID for this entity
        self._attr_unique_id = f"{coordinator.device_ip}_script_{self._script_id}_status"

        # Entity properties
        self._attr_name = f"{script['name']}"
        self._attr_has_entity_name = True

        # Device info for grouping
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_ip)},
            "name": "Shelly Script Manager",
            "manufacturer": "Shelly",
            "model": coordinator.device_type,
            "sw_version": "1.0",
        }

    @property
    def is_on(self) -> bool:
        """Return if script is running."""
        scripts = self.coordinator.data.get("scripts", [])
        for script in scripts:
            if script["id"] == self._script_id:
                return script.get("running", False)
        return False

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional attributes."""
        scripts = self.coordinator.data.get("scripts", [])
        for script in scripts:
            if script["id"] == self._script_id:
                return {
                    "script_id": script["id"],
                    "memory_used": script.get("mem_used", 0),
                    "memory_free": script.get("mem_free", 0),
                    "memory_peak": script.get("mem_peak", 0),
                }
        return {}

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        return "mdi:play-circle" if self.is_on else "mdi:stop-circle"

    async def async_turn_on(self, **kwargs) -> None:
        """Start the script."""
        success = await self.coordinator.start_script(self._script_id)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Stop the script."""
        success = await self.coordinator.stop_script(self._script_id)
        if success:
            await self.coordinator.async_request_refresh()


class ScriptAutostartSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to control script autostart (run on startup)."""

    def __init__(self, coordinator: ShABmanCoordinator, script: dict) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)

        self._script_id = script["id"]
        self._script_name = script["name"]

        # Unique ID for this entity
        self._attr_unique_id = f"{coordinator.device_ip}_script_{self._script_id}_autostart"

        # Entity properties
        self._attr_name = f"{script['name']} Run on Startup"
        self._attr_has_entity_name = True

        # Device info for grouping
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.device_ip)},
            "name": "Shelly Script Manager",
            "manufacturer": "Shelly",
            "model": coordinator.device_type,
            "sw_version": "1.0",
        }

    @property
    def is_on(self) -> bool:
        """Return if script autostart is enabled."""
        scripts = self.coordinator.data.get("scripts", [])
        for script in scripts:
            if script["id"] == self._script_id:
                return script.get("enabled", False)
        return False

    @property
    def icon(self) -> str:
        """Return icon based on state."""
        return "mdi:power" if self.is_on else "mdi:power-off"

    @property
    def entity_category(self) -> EntityCategory:
        """Set entity category to config."""
        return EntityCategory.CONFIG

    async def async_turn_on(self, **kwargs) -> None:
        """Enable script autostart."""
        success = await self.coordinator.set_script_config(self._script_id, enabled=True)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        """Disable script autostart."""
        success = await self.coordinator.set_script_config(self._script_id, enabled=False)
        if success:
            await self.coordinator.async_request_refresh()
