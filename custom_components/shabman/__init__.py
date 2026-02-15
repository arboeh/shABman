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

PLATFORMS: list[str] = []

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
            f"Successfully set up shABman for device {entry.data.get('device_id')}"
        )
    except Exception as err:
        _LOGGER.error(f"Error during first refresh: {err}", exc_info=True)
        return False

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register services only once
    if not hass.services.has_service(DOMAIN, SERVICE_UPLOAD_SCRIPT):

        async def handle_upload_script(call: ServiceCall) -> None:
            """Handle upload script service call."""
            device_id = call.data["device_id"]
            name = call.data["name"]
            code = call.data["code"]

            # Find coordinator for this device
            coord = None
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if isinstance(coordinator, ShABmanCoordinator):
                    if coordinator.config_entry.data.get("device_id") == device_id:
                        coord = coordinator
                        break

            if not coord:
                _LOGGER.error(f"Device {device_id} not found")
                return

            result = await coord.upload_script(name, code)
            if result:
                _LOGGER.info(f"Successfully uploaded script '{name}'")
                await coord.async_request_refresh()
            else:
                _LOGGER.error(f"Failed to upload script '{name}'")

        async def handle_delete_script(call: ServiceCall) -> None:
            """Handle delete script service call."""
            device_id = call.data["device_id"]
            script_id = call.data["script_id"]

            # Find coordinator for this device
            coord = None
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if isinstance(coordinator, ShABmanCoordinator):
                    if coordinator.config_entry.data.get("device_id") == device_id:
                        coord = coordinator
                        break

            if not coord:
                _LOGGER.error(f"Device {device_id} not found")
                return

            result = await coord.delete_script(script_id)
            if result:
                _LOGGER.info(f"Successfully deleted script {script_id}")
                await coord.async_request_refresh()
            else:
                _LOGGER.error(f"Failed to delete script {script_id}")

        async def handle_list_scripts(call: ServiceCall) -> None:
            """Handle list scripts service call."""
            device_id = call.data["device_id"]

            # Find coordinator for this device
            coord = None
            for entry_id, coordinator in hass.data[DOMAIN].items():
                if isinstance(coordinator, ShABmanCoordinator):
                    if coordinator.config_entry.data.get("device_id") == device_id:
                        coord = coordinator
                        break

            if not coord:
                _LOGGER.error(f"Device {device_id} not found")
                return

            scripts = coord.data.get("scripts", [])
            _LOGGER.info(f"Scripts on device {device_id}: {scripts}")

            # Also return via event for automation use
            hass.bus.async_fire(
                f"{DOMAIN}_scripts_listed", {"device_id": device_id, "scripts": scripts}
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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
