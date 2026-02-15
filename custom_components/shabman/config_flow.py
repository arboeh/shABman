"""Config flow for shABman integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN

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

    # No device type check - assume if we can connect, scripting is available

    return {
        "title": device_id,
        "device_type": device_type,
        "device_id": device_id,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for shABman."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
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
    ) -> OptionsFlow:
        """Get the options flow for this handler."""
        return OptionsFlow(config_entry)


class OptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for shABman."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry  # ← Umbenennen zu _config_entry
        self._script_id_to_delete: int | None = None

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options - main menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["upload_script", "delete_script", "list_scripts"],
        )

    async def async_step_upload_script(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Upload a new script."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Get coordinator
            from .coordinator import ShABmanCoordinator

            coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][
                self._config_entry.entry_id  # ← Ändern zu _config_entry
            ]

            name = user_input["name"]
            code = user_input["code"]

            result = await coordinator.upload_script(name, code)
            if result:
                await coordinator.async_request_refresh()
                return self.async_create_entry(title="", data={})
            else:
                errors["base"] = "upload_failed"

        return self.async_show_form(
            step_id="upload_script",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): str,
                    vol.Required("code"): selector.TextSelector(
                        selector.TextSelectorConfig(
                            multiline=True,
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_delete_script(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Delete a script - select which one."""
        from .coordinator import ShABmanCoordinator

        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][
            self._config_entry.entry_id  # ← Ändern zu _config_entry
        ]

        scripts = coordinator.data.get("scripts", [])

        if not scripts:
            return self.async_abort(reason="no_scripts")

        if user_input is not None:
            script_id = int(user_input["script"])
            self._script_id_to_delete = script_id
            return await self.async_step_confirm_delete()

        # Create options for dropdown
        script_options = {
            str(script["id"]): f"{script['name']} (ID: {script['id']})"
            for script in scripts
        }

        return self.async_show_form(
            step_id="delete_script",
            data_schema=vol.Schema(
                {
                    vol.Required("script"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=str(script_id), label=label
                                )
                                for script_id, label in script_options.items()
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_confirm_delete(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Confirm deletion."""
        if user_input is not None and user_input.get("confirm"):
            from .coordinator import ShABmanCoordinator

            coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][
                self._config_entry.entry_id  # ← Ändern zu _config_entry
            ]

            result = await coordinator.delete_script(self._script_id_to_delete)
            if result:
                await coordinator.async_request_refresh()
                return self.async_create_entry(title="", data={})
            else:
                return self.async_abort(reason="delete_failed")

        return self.async_show_form(
            step_id="confirm_delete",
            data_schema=vol.Schema(
                {
                    vol.Required("confirm", default=False): bool,
                }
            ),
            description_placeholders={
                "script_id": str(self._script_id_to_delete),
            },
        )

    async def async_step_list_scripts(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show list of all scripts."""
        from .coordinator import ShABmanCoordinator

        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][
            self._config_entry.entry_id  # ← Ändern zu _config_entry
        ]

        scripts = coordinator.data.get("scripts", [])

        if not scripts:
            return self.async_abort(reason="no_scripts")

        if user_input is not None:
            script_id = int(user_input["script"])
            # Show script details
            return await self.async_step_show_script(script_id)

        # Create options for dropdown
        script_options = {
            str(script["id"]): f"{script['name']} (ID: {script['id']})"
            for script in scripts
        }

        return self.async_show_form(
            step_id="list_scripts",
            data_schema=vol.Schema(
                {
                    vol.Required("script"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=[
                                selector.SelectOptionDict(
                                    value=str(script_id), label=label
                                )
                                for script_id, label in script_options.items()
                            ],
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_show_script(self, script_id: int | None = None) -> FlowResult:
        """Show details of a specific script."""
        from .coordinator import ShABmanCoordinator

        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][
            self._config_entry.entry_id  # ← Ändern zu _config_entry
        ]

        scripts = coordinator.data.get("scripts", [])
        script = next((s for s in scripts if s["id"] == script_id), None)

        if not script:
            return self.async_abort(reason="script_not_found")

        # Show script code in read-only text area
        return self.async_show_form(
            step_id="show_script",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "code", default=script.get("code", "Code not available")
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            multiline=True,
                            type=selector.TextSelectorType.TEXT,
                        )
                    ),
                }
            ),
            description_placeholders={
                "script_name": script["name"],
                "script_id": str(script["id"]),
                "enabled": "Yes" if script.get("enable") else "No",
                "running": "Yes" if script.get("running") else "No",
            },
        )
