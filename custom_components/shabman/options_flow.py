# custom_components\shabman\options_flow.py

"""Options flow for shABman integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import DOMAIN
from .coordinator import ShABmanCoordinator

_LOGGER = logging.getLogger(__name__)


class ShABmanOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for shABman."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self._current_script_id: int | None = None
        self._current_script_code: str | None = None

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Manage the options - main menu."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["create_script", "manage_scripts", "delete_script"],
        )

    async def async_step_create_script(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Create a new script."""
        errors: dict[str, str] = {}

        if user_input is not None:
            coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]

            name = user_input["name"]
            code = user_input["code"]

            result = await coordinator.upload_script(name, code)
            if result:
                await coordinator.async_request_refresh()
                return self.async_create_entry(title="", data={})
            else:
                errors["base"] = "upload_failed"

        return self.async_show_form(
            step_id="create_script",
            data_schema=vol.Schema(
                {
                    vol.Required("name"): str,
                    vol.Required("code", default=""): selector.TemplateSelector(),
                }
            ),
            errors=errors,
        )

    async def async_step_manage_scripts(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Select a script to manage."""
        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]

        scripts = coordinator.data.get("scripts", [])

        if not scripts:
            return self.async_abort(reason="no_scripts")

        if user_input is not None:
            script_id = int(user_input["script"])
            self._current_script_id = script_id
            self._current_script_code = None  # Reset cache
            return await self.async_step_edit_script()

        # Create options for dropdown
        script_options = [
            selector.SelectOptionDict(value=str(script["id"]), label=f"{script['name']} (ID: {script['id']})")
            for script in scripts
        ]

        return self.async_show_form(
            step_id="manage_scripts",
            data_schema=vol.Schema(
                {
                    vol.Required("script"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=script_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    ),
                }
            ),
        )

    async def async_step_edit_script(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Edit a script."""
        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]

        scripts = coordinator.data.get("scripts", [])
        script = next((s for s in scripts if s["id"] == self._current_script_id), None)

        if not script:
            return self.async_abort(reason="script_not_found")

        if user_input is not None:
            name = user_input["name"]
            code = user_input["code"]

            # BACKUP: Save original script data
            backup_name = script.get("name", "")
            backup_code = self._current_script_code
            backup_id = self._current_script_id

            await self._create_script_backup(backup_id, backup_name, "edit")

            # Delete old script
            delete_success = await coordinator.delete_script(self._current_script_id)

            if not delete_success:
                errors = {"base": "update_failed"}
                return self.async_show_form(
                    step_id="edit_script",
                    data_schema=vol.Schema(
                        {
                            vol.Required("name", default=name): str,
                            vol.Required("code", default=code): selector.TemplateSelector(),
                        }
                    ),
                    errors=errors,
                    description_placeholders={
                        "script_id": str(self._current_script_id),
                        "enabled": "Ja" if script.get("enabled") else "Nein",
                        "running": "Ja" if script.get("running") else "Nein",
                    },
                )

            # Wait a bit before creating new script (give Shelly time to cleanup)
            await asyncio.sleep(1)

            # Upload new script (with retry logic)
            upload_success = await coordinator.upload_script(name, code, retry_count=3)

            if upload_success:
                _LOGGER.info(f"Successfully updated script '{name}'")
                await coordinator.async_request_refresh()
                self._current_script_code = None  # Clear cache
                return self.async_create_entry(title="", data={})
            else:
                # ROLLBACK: Restore original script
                _LOGGER.error(f"Failed to upload new version! Attempting rollback to '{backup_name}'...")

                # Wait before rollback attempt
                await asyncio.sleep(2)

                rollback_success = await coordinator.upload_script(
                    backup_name,
                    backup_code,
                    retry_count=5,  # More retries for rollback!
                )

                if rollback_success:
                    _LOGGER.warning(f"Successfully restored original script '{backup_name}' after failed update")
                    await coordinator.async_request_refresh()
                    errors = {"base": "update_failed_restored"}
                else:
                    _LOGGER.error(
                        f"CRITICAL: Failed to restore script '{backup_name}' (ID: {backup_id})! "
                        f"Backup saved to shabman_backups/ folder. "
                        f"Code length: {len(backup_code)} bytes"
                    )
                    errors = {"base": "update_failed_lost"}

                return self.async_show_form(
                    step_id="edit_script",
                    data_schema=vol.Schema(
                        {
                            vol.Required("name", default=backup_name): str,
                            vol.Required("code", default=backup_code): selector.TemplateSelector(),
                        }
                    ),
                    errors=errors,
                    description_placeholders={
                        "script_id": str(backup_id),
                        "enabled": "Ja" if script.get("enabled") else "Nein",
                        "running": "Ja" if script.get("running") else "Nein",
                    },
                )

        # Load script code on-demand (only when opening the form)
        if self._current_script_code is None:
            _LOGGER.debug(f"Loading code for script {self._current_script_id}")
            self._current_script_code = await coordinator.get_script_code(self._current_script_id)

            if self._current_script_code is None:
                self._current_script_code = "// Could not load script code"
                _LOGGER.warning(f"Failed to load code for script {self._current_script_id}")

        script_code = self._current_script_code

        return self.async_show_form(
            step_id="edit_script",
            data_schema=vol.Schema(
                {
                    vol.Required("name", default=script.get("name", "")): str,
                    vol.Required("code", default=script_code): selector.TemplateSelector(),
                }
            ),
            description_placeholders={
                "script_id": str(self._current_script_id),
                "enabled": "Ja" if script.get("enabled") else "Nein",
                "running": "Ja" if script.get("running") else "Nein",
            },
        )

    async def async_step_delete_script(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Delete a script - select which one."""
        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
        scripts = coordinator.data.get("scripts", [])

        if not scripts:
            return self.async_abort(reason="no_scripts")

        if user_input is not None:
            script_id = int(user_input["script"])
            self._current_script_id = script_id
            return await self.async_step_confirm_delete()

        # Dropdown...
        script_options = [
            selector.SelectOptionDict(value=str(script["id"]), label=f"{script['name']} (ID: {script['id']})")
            for script in scripts
        ]

        return self.async_show_form(
            step_id="delete_script",
            data_schema=vol.Schema(
                {
                    vol.Required("script"): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=script_options,
                            mode=selector.SelectSelectorMode.DROPDOWN,
                        )
                    )
                }
            ),
        )

    async def async_step_confirm_delete(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Confirm script deletion."""
        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]
        scripts = coordinator.data.get("scripts", [])
        script = next((s for s in scripts if s["id"] == self._current_script_id), None)

        if not script:
            return self.async_abort(reason="script_not_found")

        if user_input is not None:
            # BACKUP
            backup_name = script.get("name", "")
            backup_id = self._current_script_id
            await self._create_script_backup(backup_id, backup_name, "delete")

            # Delete
            result = await coordinator.delete_script(self._current_script_id)
            if result:
                await coordinator.async_request_refresh()
                return self.async_create_entry(title="", data={})
            else:
                return self.async_abort(reason="delete_failed")

        return self.async_show_form(
            step_id="confirm_delete",
            data_schema=vol.Schema({}),
            description_placeholders={
                "script_name": script.get("name", "Unknown"),
                "script_id": str(self._current_script_id),
            },
        )

    async def _create_script_backup(
        self, script_id: int, script_name: str, reason: str = "manual", max_backups: int = 10
    ) -> bool:
        """Create persistent backup with automatic retention."""
        coordinator: ShABmanCoordinator = self.hass.data[DOMAIN][self._config_entry.entry_id]

        script_code = await coordinator.get_script_code(script_id)
        if script_code is None:
            _LOGGER.warning(f"Cannot backup script {script_id}: no code")
            return False

        try:
            import json
            from datetime import datetime
            from pathlib import Path

            backup_dir = Path(self.hass.config.path("shabman_backups"))
            backup_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"script_{script_id}_{reason}_{timestamp}.json"

            backup_data = {
                "id": script_id,
                "name": script_name,
                "code": script_code,
                "timestamp": timestamp,
                "reason": reason,
            }

            with open(backup_file, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)

            # RETENTION: Max 'max_backups' pro Script behalten
            backup_pattern = backup_dir / f"script_{script_id}_*.json"
            existing = sorted(backup_pattern.glob("*"), key=lambda x: x.stat().st_mtime)

            while len(existing) >= max_backups:
                oldest = existing.pop(0)
                oldest.unlink()
                _LOGGER.debug(f"Retention cleanup: removed {oldest}")

            _LOGGER.info(f"Backup created ({len(existing) + 1}/{max_backups}): {backup_file.name}")
            return True

        except Exception as err:
            _LOGGER.error(f"Backup failed for script {script_id}: {err}")
            return False
