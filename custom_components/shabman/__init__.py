# custom_components\shabman\__init__.py

"""The shABman integration."""

from __future__ import annotations

import logging

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .coordinator import ShABmanCoordinator

_LOGGER = logging.getLogger(__name__)
try:
    from .__version__ import __version__

    _LOGGER.info(f"shABman v{__version__} loaded")
except ImportError:
    pass

# Platforms to set up
PLATFORMS = ["switch", "sensor"]

# Service schemas
SERVICE_UPLOAD_SCRIPT = "upload_script"
SERVICE_DELETE_SCRIPT = "delete_script"
SERVICE_LIST_SCRIPTS = "list_scripts"

UPLOAD_SCRIPT_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Required("name"): cv.string,
        vol.Required("code"): cv.string,
    }
)

DELETE_SCRIPT_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
        vol.Required("script_id"): cv.positive_int,
    }
)

LIST_SCRIPTS_SCHEMA = vol.Schema(
    {
        vol.Required("device_id"): cv.string,
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the shABman component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up shABman from a config entry."""
    # Prevent double setup (important for tests)
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        _LOGGER.debug("Entry %s already set up, skipping", entry.entry_id)
        return True

    hass.data.setdefault(DOMAIN, {})

    coordinator = ShABmanCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
        _LOGGER.info(
            "Successfully set up shABman for device %s",
            entry.data.get("device_id"),
        )
    except Exception as err:
        _LOGGER.error("Error during first refresh: %s", err, exc_info=True)
        return False

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Start WebSocket listener for real-time updates
    await coordinator.async_start_websocket()  # 🔥 NEU

    # Forward entry setup to platforms (creates entities)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options flow
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register services only once (global services)
    if not hass.services.has_service(DOMAIN, SERVICE_UPLOAD_SCRIPT):
        _register_services(hass)

    return True


def _register_services(hass: HomeAssistant) -> None:
    """Register shABman services."""

    async def handle_upload_script(call: ServiceCall) -> None:
        """Handle upload script service call."""
        device_id = call.data["device_id"]
        name = call.data["name"]
        code = call.data["code"]

        coordinator = _find_coordinator_by_device_id(hass, device_id)
        if not coordinator:
            _LOGGER.error("Device %s not found", device_id)
            return

        result = await coordinator.upload_script(name, code)
        if result:
            _LOGGER.info("Successfully uploaded script '%s' to device %s", name, device_id)
            await coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to upload script '%s' to device %s", name, device_id)

    async def handle_delete_script(call: ServiceCall) -> None:
        """Handle delete script service call."""
        device_id = call.data["device_id"]
        script_id = call.data["script_id"]

        coordinator = _find_coordinator_by_device_id(hass, device_id)
        if not coordinator:
            _LOGGER.error("Device %s not found", device_id)
            return

        result = await coordinator.delete_script(script_id)
        if result:
            _LOGGER.info("Successfully deleted script %s from device %s", script_id, device_id)
            await coordinator.async_request_refresh()
        else:
            _LOGGER.error("Failed to delete script %s from device %s", script_id, device_id)

    async def handle_list_scripts(call: ServiceCall) -> None:
        """Handle list scripts service call."""
        device_id = call.data["device_id"]

        coordinator = _find_coordinator_by_device_id(hass, device_id)
        if not coordinator:
            _LOGGER.error("Device %s not found", device_id)
            return

        scripts = coordinator.data.get("scripts", [])
        _LOGGER.info("Device %s has %d scripts", device_id, len(scripts))

        # Fire event for automation use
        hass.bus.async_fire(
            f"{DOMAIN}_scripts_listed",
            {"device_id": device_id, "scripts": scripts},
        )

    hass.services.async_register(
        DOMAIN,
        SERVICE_UPLOAD_SCRIPT,
        handle_upload_script,
        schema=UPLOAD_SCRIPT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_DELETE_SCRIPT,
        handle_delete_script,
        schema=DELETE_SCRIPT_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_LIST_SCRIPTS,
        handle_list_scripts,
        schema=LIST_SCRIPTS_SCHEMA,
    )

    _LOGGER.info("Registered shABman services")


def _find_coordinator_by_device_id(hass: HomeAssistant, device_id: str):
    """Find coordinator by device_id."""
    for _entry_id, coordinator in hass.data[DOMAIN].items():
        # Use device_id stored in coordinator
        if hasattr(coordinator, "device_id") and coordinator.device_id == device_id:
            return coordinator
        # Fallback: check config_entry
        if coordinator.config_entry and coordinator.config_entry.data.get("device_id") == device_id:
            return coordinator
    return None


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Check if entry exists in hass.data
    if entry.entry_id not in hass.data.get(DOMAIN, {}):
        _LOGGER.warning("Entry %s not found in hass.data, skipping unload", entry.entry_id)
        return True

    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Cancel WebSocket task
    if hasattr(coordinator, "_ws_task") and coordinator._ws_task:
        coordinator._ws_task.cancel()
        try:
            await coordinator._ws_task
        except Exception as e:
            _LOGGER.debug("Error canceling WebSocket task: %s", e)

    # Unload platforms
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
