# custom_components\shabman\config_flow.py

"""Config flow for shABman integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN
from .options_flow import ShABmanOptionsFlow

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_DEVICE_IP): str,
    }
)


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class UnsupportedDevice(Exception):
    """Error to indicate device type is unsupported."""


async def validate_input(hass, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    device_ip = data[CONF_DEVICE_IP]

    # Get device info directly
    url = f"http://{device_ip}/rpc/Shelly.GetDeviceInfo"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    raise CannotConnect

                device_info = await response.json()
    except Exception as err:
        _LOGGER.error(f"Connection error: {err}")
        raise CannotConnect

    device_type = device_info.get("model", device_info.get("app", "unknown"))
    device_id = device_info.get("id", "unknown")

    return {
        "title": device_id,
        "device_type": device_type,
        "device_id": device_id,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for shABman."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except UnsupportedDevice:
                errors["base"] = "unsupported_device"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["device_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        **user_input,
                        CONF_DEVICE_TYPE: info["device_type"],
                        "device_id": info["device_id"],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> ShABmanOptionsFlow:
        """Get the options flow for this handler."""
        return ShABmanOptionsFlow(config_entry)
