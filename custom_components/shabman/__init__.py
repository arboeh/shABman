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


def _find_coordinator_by_device_id(hass: HomeAssistant, device_id: str) -> ShABmanCoordinator | None:
    """Find coordinator by device_id."""
    for coordinator in hass.data[DOMAIN].values():
        if isinstance(coordinator, ShABmanCoordinator):
            if coordinator.config_entry.data.get("device_id") == device_id:
                return coordinator
    return None


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    # Shutdown WebSocket
    await coordinator.async_shutdown()  # 🔥 NEU

    # Unload platforms first
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Only unregister services if no more entries exist
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, SERVICE_UPLOAD_SCRIPT)
            hass.services.async_remove(DOMAIN, SERVICE_DELETE_SCRIPT)
            hass.services.async_remove(DOMAIN, SERVICE_LIST_SCRIPTS)
            _LOGGER.info("Unregistered shABman services")

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
