# custom_components\shabman\coordinator.py

"""Coordinator for shABman."""

import asyncio
import logging
from datetime import timedelta

import aiohttp
from aiohttp import WSMsgType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ShABmanCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Shelly device."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.config_entry = entry
        self.device_ip = entry.data[CONF_DEVICE_IP]
        self.device_type = entry.data.get(CONF_DEVICE_TYPE, "unknown")

        self._ws_task = None  # WebSocket listener task
        self._ws_session = None

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),  # Fallback polling
        )

    async def _async_update_data(self) -> dict[str, any]:
        """Fetch data from the device."""
        try:
            scripts = await self.list_scripts()

            # Load status for all scripts in parallel
            status_tasks = [self.get_script_status(script["id"]) for script in scripts]
            statuses = await asyncio.gather(*status_tasks, return_exceptions=True)

            # Process scripts with their status
            running_count = 0
            enabled_count = 0

            for script, status in zip(scripts, statuses):
                # "enable" kommt aus Script.List, nicht GetStatus!
                script_enabled = script.get("enable", False)  # 🔥 Aus List!

                # Handle status (running, mem_used, etc.)
                if isinstance(status, Exception) or not status:
                    _LOGGER.warning(f"Failed to load status for script {script['id']}")
                    script["running"] = False
                    script["mem_used"] = 0
                else:
                    script["running"] = status["running"]
                    script["mem_used"] = status["mem_used"]
                    script["mem_free"] = status.get("mem_free", 0)
                    script["mem_peak"] = status.get("mem_peak", 0)

                # enabled aus Script.List übernehmen!
                script["enabled"] = script_enabled

                if script.get("running"):
                    running_count += 1
                if script.get("enabled"):
                    enabled_count += 1

            _LOGGER.debug(
                f"Updated data: {len(scripts)} scripts " f"({running_count} running, {enabled_count} autostart enabled)"
            )

            return {
                "scripts": scripts,
                "device_type": self.device_type,
                "running_count": running_count,
                "enabled_count": enabled_count,
            }
        except Exception as err:
            _LOGGER.error(f"Error updating data: {err}")
            raise UpdateFailed(f"Error communicating with device: {err}")

    async def async_start_websocket(self) -> None:
        """Start WebSocket connection for real-time updates."""
        if self._ws_task:
            return  # Already running

        self._ws_task = asyncio.create_task(self._websocket_listener())
        _LOGGER.info("Started WebSocket listener for real-time updates")

    async def _websocket_listener(self) -> None:
        """Listen for WebSocket events from Shelly."""
        ws_url = f"ws://{self.device_ip}/rpc"

        while True:
            try:
                self._ws_session = aiohttp.ClientSession()
                async with self._ws_session.ws_connect(ws_url) as ws:
                    _LOGGER.info("WebSocket connected to Shelly")

                    async for msg in ws:
                        if msg.type == WSMsgType.TEXT:
                            data = msg.json()

                            # Check if it's a script notification
                            method = data.get("method")
                            if method == "NotifyStatus":
                                params = data.get("params", {})
                                # Script status changed
                                if "script:id" in str(params):
                                    _LOGGER.debug(f"Script status changed: {params}")
                                    await self.async_request_refresh()

                        elif msg.type == WSMsgType.ERROR:
                            _LOGGER.error("WebSocket error")
                            break
                        elif msg.type == WSMsgType.CLOSED:
                            _LOGGER.warning("WebSocket closed")
                            break

            except Exception as err:
                _LOGGER.error(f"WebSocket error: {err}")

            finally:
                if self._ws_session:
                    await self._ws_session.close()
                    self._ws_session = None

            # Reconnect after 5 seconds
            await asyncio.sleep(5)

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and WebSocket."""
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass

        if self._ws_session:
            await self._ws_session.close()

    async def list_scripts(self) -> list:
        """List all scripts on the device."""
        try:
            url = f"http://{self.device_ip}/rpc/Script.List"

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        scripts = data.get("scripts", [])
                        _LOGGER.info(f"Found {len(scripts)} scripts on device")
                        return scripts
                    else:
                        _LOGGER.error(f"Failed to list scripts: {response.status}")
                        return []
        except Exception as err:
            _LOGGER.error(f"Error listing scripts: {err}")
            return []

    async def get_script_code(self, script_id: int) -> str | None:
        """Get the code of a specific script."""
        try:
            url = f"http://{self.device_ip}/rpc/Script.GetCode"
            params = {"id": script_id}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", "")
                    else:
                        _LOGGER.error(f"Failed to get script code: {response.status}")
                        return None
        except Exception as err:
            _LOGGER.error(f"Error getting script code: {err}")
            return None

    async def get_script_status(self, script_id: int) -> dict | None:
        """Get detailed script status."""
        try:
            url = f"http://{self.device_ip}/rpc/Script.GetStatus"
            params = {"id": script_id}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()

                        status = {
                            "id": data.get("id"),
                            "running": data.get("running", False),
                            "enabled": data.get("enabled", False),
                            "mem_used": data.get("mem_used", 0),
                            "mem_free": data.get("mem_free", 0),
                            "mem_peak": data.get("mem_peak", 0),
                        }

                        _LOGGER.debug(
                            f"Script {script_id} status: " f"running={status['running']}, enabled={status['enabled']}"
                        )

                        return status
                    else:
                        _LOGGER.error(f"Failed to get script status: {response.status}")
                        return None
        except Exception as err:
            _LOGGER.error(f"Error getting script status {script_id}: {err}")
            return None

    async def upload_script(self, name: str, code: str, retry_count: int = 3) -> bool:
        """Upload a new script to the device with chunking and retry logic."""

        for attempt in range(retry_count):
            try:
                url = f"http://{self.device_ip}/rpc/Script.Create"
                payload = {"name": name}

                async with aiohttp.ClientSession() as session:
                    # First create the script
                    async with session.post(url, json=payload, timeout=10) as response:
                        if response.status != 200:
                            _LOGGER.error(
                                f"Failed to create script (attempt {attempt + 1}/{retry_count}): {response.status}"
                            )
                            if attempt < retry_count - 1:
                                await asyncio.sleep(1)
                                continue
                            return False

                        data = await response.json()
                        script_id = data.get("id")

                        if not script_id:
                            _LOGGER.error("No script ID returned")
                            return False

                    _LOGGER.info(f"Created script '{name}' with ID {script_id}")

                    # Upload code in chunks
                    chunk_size = 4096
                    code_bytes = code.encode("utf-8")
                    code_length = len(code_bytes)
                    offset = 0

                    while offset < code_length:
                        chunk_bytes = code_bytes[offset : offset + chunk_size]
                        chunk = chunk_bytes.decode("utf-8", errors="ignore")
                        append = offset > 0

                        url = f"http://{self.device_ip}/rpc/Script.PutCode"
                        payload = {
                            "id": script_id,
                            "code": chunk,
                            "append": append,
                        }

                        async with session.post(url, json=payload, timeout=15) as response:
                            if response.status != 200:
                                _LOGGER.error(
                                    f"Failed to upload chunk at offset {offset} "
                                    f"(attempt {attempt + 1}/{retry_count}): {response.status}"
                                )
                                await self.delete_script(script_id)

                                if attempt < retry_count - 1:
                                    await asyncio.sleep(2)
                                    break
                                return False

                        _LOGGER.debug(
                            f"Uploaded chunk {offset}-{offset + len(chunk_bytes)} of {code_length} bytes "
                            f"({int((offset + len(chunk_bytes)) / code_length * 100)}%)"
                        )
                        offset += len(chunk_bytes)
                        await asyncio.sleep(0.1)

                    chunk_count = (code_length // chunk_size) + 1
                    _LOGGER.info(
                        f"Successfully uploaded script '{name}' with ID {script_id} "
                        f"({code_length} bytes in {chunk_count} chunks)"
                    )
                    return True

            except Exception as err:
                _LOGGER.error(f"Error uploading script (attempt {attempt + 1}/{retry_count}): {err}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2)
                else:
                    return False

        return False

    async def delete_script(self, script_id: int) -> bool:
        """Delete a script from the device."""
        try:
            url = f"http://{self.device_ip}/rpc/Script.Delete"
            payload = {"id": script_id}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        _LOGGER.info(f"Successfully deleted script {script_id}")
                        return True
                    else:
                        _LOGGER.error(f"Failed to delete script: {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error deleting script: {err}")
            return False

    async def start_script(self, script_id: int) -> bool:
        """Start a script on the device."""
        try:
            url = f"http://{self.device_ip}/rpc/Script.Start"
            payload = {"id": script_id}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        was_running = data.get("was_running", False)

                        if was_running:
                            _LOGGER.info(f"Script {script_id} was already running")
                        else:
                            _LOGGER.info(f"Successfully started script {script_id}")

                        return True
                    else:
                        _LOGGER.error(f"Failed to start script: {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error starting script {script_id}: {err}")
            return False

    async def stop_script(self, script_id: int) -> bool:
        """Stop a script on the device."""
        try:
            url = f"http://{self.device_ip}/rpc/Script.Stop"
            payload = {"id": script_id}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        was_running = data.get("was_running", False)

                        if not was_running:
                            _LOGGER.info(f"Script {script_id} was not running")
                        else:
                            _LOGGER.info(f"Successfully stopped script {script_id}")

                        return True
                    else:
                        _LOGGER.error(f"Failed to stop script: {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error stopping script {script_id}: {err}")
            return False

    async def set_script_config(self, script_id: int, enabled: bool) -> bool:
        """Enable or disable script autostart."""
        try:
            url = f"http://{self.device_ip}/rpc/Script.SetConfig"
            payload = {"id": script_id, "config": {"enable": enabled}}

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as response:
                    if response.status == 200:
                        _LOGGER.info(f"Script {script_id} autostart " f"{'enabled' if enabled else 'disabled'}")
                        return True
                    else:
                        _LOGGER.error(f"Failed to set script config: {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error setting script config {script_id}: {err}")
            return False
