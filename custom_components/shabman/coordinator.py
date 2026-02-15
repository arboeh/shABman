"""DataUpdateCoordinator for shABman."""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ShABmanCoordinator(DataUpdateCoordinator):
    """Class to manage fetching shABman data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry
        self.device_ip = entry.data[CONF_DEVICE_IP]
        self.device_type = entry.data.get(CONF_DEVICE_TYPE, "unknown")

        self._client = None
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from Shelly device."""
        try:
            scripts = await self.fetch_scripts()
            _LOGGER.debug(f"Successfully fetched {len(scripts)} scripts")
            return {"scripts": scripts}
        except Exception as err:
            _LOGGER.error(f"Error fetching data: {err}", exc_info=True)
            raise UpdateFailed(f"Error fetching data: {err}")

    async def fetch_scripts(self) -> list[dict[str, Any]]:
        """Fetch scripts from the Shelly device."""
        url = f"http://{self.device_ip}/rpc/Script.List"

        try:
            _LOGGER.debug(f"Fetching scripts from {url}")
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=10)
                ) as resp:
                    if resp.status != 200:
                        _LOGGER.error(f"Failed to fetch scripts, status: {resp.status}")
                        raise UpdateFailed(
                            f"Error fetching scripts: HTTP {resp.status}"
                        )

                    data = await resp.json()
                    scripts = data.get("scripts", [])
                    _LOGGER.info(f"Found {len(scripts)} scripts on device")
                    return scripts

        except aiohttp.ClientError as err:
            _LOGGER.error(f"Connection error: {err}")
            raise UpdateFailed(f"Connection error: {err}")

    async def upload_script(self, name: str, code: str) -> bool:
        """Upload a script to the Shelly device."""
        url = f"http://{self.device_ip}/rpc/Script.Create"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={"name": name, "code": code},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                return resp.status == 200

    async def delete_script(self, script_id: int) -> bool:
        """Delete a script from the Shelly device."""
        url = f"http://{self.device_ip}/rpc/Script.Delete"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json={"id": script_id}, timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                return resp.status == 200
