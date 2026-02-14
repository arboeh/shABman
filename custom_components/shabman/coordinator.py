"""DataUpdateCoordinator for shABman."""
from __future__ import annotations

import logging
from datetime import timedelta

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, CONF_DEVICE_IP, UPDATE_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ShABmanCoordinator(DataUpdateCoordinator):
    """Class to manage fetching shABman data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize."""
        self.entry = entry
        self.device_ip = entry.data[CONF_DEVICE_IP]
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            return await self._fetch_scripts()
        except Exception as exception:
            raise UpdateFailed() from exception

    async def _fetch_scripts(self) -> dict:
        """Fetch scripts from Shelly device."""
        url = f"http://{self.device_ip}/rpc/Script.List"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"Error fetching scripts: {resp.status}")
                
                data = await resp.json()
                return data.get("scripts", [])

    async def upload_script(self, name: str, code: str) -> bool:
        """Upload a script to the Shelly device."""
        create_url = f"http://{self.device_ip}/rpc/Script.Create"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                create_url,
                json={"name": name},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to create script: %s", resp.status)
                    return False
                
                result = await resp.json()
                script_id = result.get("id")
        
        put_url = f"http://{self.device_ip}/rpc/Script.PutCode"
        async with aiohttp.ClientSession() as session:
            async with session.post(
                put_url,
                json={"id": script_id, "code": code, "append": False},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to upload script code: %s", resp.status)
                    return False
        
        await self.async_request_refresh()
        return True

    async def delete_script(self, script_id: int) -> bool:
        """Delete a script from the Shelly device."""
        url = f"http://{self.device_ip}/rpc/Script.Delete"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={"id": script_id},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                if resp.status != 200:
                    _LOGGER.error("Failed to delete script: %s", resp.status)
                    return False
        
        await self.async_request_refresh()
        return True
