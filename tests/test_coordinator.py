"""Test the shABman coordinator."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import WSMsgType
from aioresponses import aioresponses
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import UpdateFailed
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shabman.const import CONF_DEVICE_IP, CONF_DEVICE_TYPE, DOMAIN
from custom_components.shabman.coordinator import ShABmanCoordinator


@pytest.fixture
def mock_config_entry(hass):
    """Create a mock config entry."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="Test Shelly",
        data={
            CONF_DEVICE_IP: "192.168.1.100",
            CONF_DEVICE_TYPE: "SNSW-001X16EU",
            "device_id": "test123",
        },
        unique_id="test123",
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_coordinator(hass, mock_config_entry):
    """Create a coordinator."""
    coordinator = ShABmanCoordinator(hass, mock_config_entry)
    return coordinator


# ===== Real HTTP Tests with aioresponses =====


async def test_list_scripts_success(hass: HomeAssistant, mock_coordinator):
    """Test listing scripts with real HTTP mock."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/rpc/Script.List",
            payload={
                "scripts": [
                    {"id": 1, "name": "test1", "enable": True},
                    {"id": 2, "name": "test2", "enable": False},
                ]
            },
        )

        scripts = await mock_coordinator.list_scripts()

        assert len(scripts) == 2
        assert scripts[0]["name"] == "test1"


async def test_list_scripts_error(hass: HomeAssistant, mock_coordinator):
    """Test listing scripts with HTTP error."""
    with aioresponses() as m:
        m.get("http://192.168.1.100/rpc/Script.List", status=500)

        scripts = await mock_coordinator.list_scripts()

        assert scripts == []


async def test_list_scripts_exception(hass: HomeAssistant, mock_coordinator):
    """Test listing scripts with exception."""
    with aioresponses() as m:
        m.get("http://192.168.1.100/rpc/Script.List", exception=ConnectionError())

        scripts = await mock_coordinator.list_scripts()

        assert scripts == []


async def test_get_script_code_success(hass: HomeAssistant, mock_coordinator):
    """Test getting script code."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/rpc/Script.GetCode?id=1",
            payload={"data": "let x = 1;"},
        )

        code = await mock_coordinator.get_script_code(1)

        assert code == "let x = 1;"


async def test_get_script_code_error(hass: HomeAssistant, mock_coordinator):
    """Test getting script code with error."""
    with aioresponses() as m:
        m.get("http://192.168.1.100/rpc/Script.GetCode?id=1", status=404)

        code = await mock_coordinator.get_script_code(1)

        assert code is None


async def test_get_script_status_success(hass: HomeAssistant, mock_coordinator):
    """Test getting script status."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/rpc/Script.GetStatus?id=1",
            payload={
                "id": 1,
                "running": True,
                "enabled": True,
                "mem_used": 1024,
                "mem_free": 2048,
                "mem_peak": 1500,
            },
        )

        status = await mock_coordinator.get_script_status(1)

        assert status["running"] is True
        assert status["enabled"] is True
        assert status["mem_used"] == 1024


async def test_get_script_status_error(hass: HomeAssistant, mock_coordinator):
    """Test getting script status with error."""
    with aioresponses() as m:
        m.get("http://192.168.1.100/rpc/Script.GetStatus?id=1", status=500)

        status = await mock_coordinator.get_script_status(1)

        assert status is None


async def test_start_script(hass: HomeAssistant, mock_coordinator):
    """Test starting a script."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/rpc/Script.Start",
            payload={"was_running": False},
        )

        result = await mock_coordinator.start_script(1)

        assert result is True


async def test_start_script_already_running(hass: HomeAssistant, mock_coordinator):
    """Test starting a script that's already running."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/rpc/Script.Start",
            payload={"was_running": True},
        )

        result = await mock_coordinator.start_script(1)

        assert result is True


async def test_start_script_error(hass: HomeAssistant, mock_coordinator):
    """Test starting a script with error."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Start", status=500)

        result = await mock_coordinator.start_script(1)

        assert result is False


async def test_start_script_exception(hass: HomeAssistant, mock_coordinator):
    """Test starting a script with exception."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Start", exception=ConnectionError())

        result = await mock_coordinator.start_script(1)

        assert result is False


async def test_stop_script(hass: HomeAssistant, mock_coordinator):
    """Test stopping a script."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/rpc/Script.Stop",
            payload={"was_running": True},
        )

        result = await mock_coordinator.stop_script(1)

        assert result is True


async def test_stop_script_not_running(hass: HomeAssistant, mock_coordinator):
    """Test stopping a script that wasn't running."""
    with aioresponses() as m:
        m.post(
            "http://192.168.1.100/rpc/Script.Stop",
            payload={"was_running": False},
        )

        result = await mock_coordinator.stop_script(1)

        assert result is True


async def test_stop_script_error(hass: HomeAssistant, mock_coordinator):
    """Test stopping a script with error."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Stop", status=500)

        result = await mock_coordinator.stop_script(1)

        assert result is False


async def test_delete_script(hass: HomeAssistant, mock_coordinator):
    """Test script deletion."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Delete", payload={})

        result = await mock_coordinator.delete_script(1)

        assert result is True


async def test_delete_script_error(hass: HomeAssistant, mock_coordinator):
    """Test script deletion with error."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Delete", status=404)

        result = await mock_coordinator.delete_script(1)

        assert result is False


async def test_delete_script_exception(hass: HomeAssistant, mock_coordinator):
    """Test script deletion with exception."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Delete", exception=ConnectionError())

        result = await mock_coordinator.delete_script(1)

        assert result is False


async def test_set_script_config(hass: HomeAssistant, mock_coordinator):
    """Test setting script configuration (autostart)."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.SetConfig", payload={})

        result = await mock_coordinator.set_script_config(1, enabled=True)

        assert result is True


async def test_set_script_config_error(hass: HomeAssistant, mock_coordinator):
    """Test setting script config with error."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.SetConfig", status=500)

        result = await mock_coordinator.set_script_config(1, enabled=False)

        assert result is False


async def test_set_script_config_exception(hass: HomeAssistant, mock_coordinator):
    """Test setting script config with exception."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.SetConfig", exception=ConnectionError())

        result = await mock_coordinator.set_script_config(1, enabled=True)

        assert result is False


# ===== Upload Script with Chunking =====


async def test_upload_script_small(hass: HomeAssistant, mock_coordinator):
    """Test uploading a small script (no chunking)."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Create", payload={"id": 1})
        m.post("http://192.168.1.100/rpc/Script.PutCode", payload={})

        result = await mock_coordinator.upload_script("test", "console.log('hello');")

        assert result is True


async def test_upload_script_large_chunking(hass: HomeAssistant, mock_coordinator):
    """Test uploading a large script with chunking."""
    large_code = "x" * 10000  # Larger than 4096 chunk size

    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Create", payload={"id": 1})
        # Mock multiple PutCode calls (aioresponses allows repeated calls)
        m.post("http://192.168.1.100/rpc/Script.PutCode", payload={}, repeat=True)

        result = await mock_coordinator.upload_script("large_script", large_code)

        assert result is True


async def test_upload_script_create_fails(hass: HomeAssistant, mock_coordinator):
    """Test upload when Script.Create fails."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Create", status=500, repeat=True)

        result = await mock_coordinator.upload_script("test", "code", retry_count=2)

        assert result is False


async def test_upload_script_no_id_returned(hass: HomeAssistant, mock_coordinator):
    """Test upload when no script ID is returned."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Create", payload={})

        result = await mock_coordinator.upload_script("test", "code")

        assert result is False


async def test_upload_script_putcode_fails_with_retry(hass: HomeAssistant, mock_coordinator):
    """Test upload with PutCode failure and retry logic."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Create", payload={"id": 1}, repeat=True)
        m.post("http://192.168.1.100/rpc/Script.PutCode", status=500, repeat=True)
        m.post("http://192.168.1.100/rpc/Script.Delete", payload={}, repeat=True)

        result = await mock_coordinator.upload_script("test", "code", retry_count=1)

        assert result is False


async def test_upload_script_exception_with_retry(hass: HomeAssistant, mock_coordinator):
    """Test upload with exception and retry logic."""
    with aioresponses() as m:
        m.post("http://192.168.1.100/rpc/Script.Create", exception=ConnectionError(), repeat=True)

        result = await mock_coordinator.upload_script("test", "code", retry_count=2)

        assert result is False


# ===== Update Coordinator Data =====


async def test_coordinator_update_data(hass: HomeAssistant, mock_coordinator):
    """Test full coordinator data update."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/rpc/Script.List",
            payload={
                "scripts": [
                    {"id": 1, "name": "test1", "enable": True},
                    {"id": 2, "name": "test2", "enable": False},
                ]
            },
        )
        # Mock GetStatus for both scripts
        m.get(
            "http://192.168.1.100/rpc/Script.GetStatus?id=1",
            payload={"id": 1, "running": True, "enabled": True, "mem_used": 1024, "mem_free": 2048, "mem_peak": 1500},
        )
        m.get(
            "http://192.168.1.100/rpc/Script.GetStatus?id=2",
            payload={"id": 2, "running": False, "enabled": False, "mem_used": 0, "mem_free": 2048, "mem_peak": 0},
        )

        data = await mock_coordinator._async_update_data()

        assert len(data["scripts"]) == 2
        assert data["running_count"] == 1
        assert data["enabled_count"] == 1
        assert data["scripts"][0]["running"] is True


async def test_coordinator_update_failed(hass: HomeAssistant, mock_coordinator):
    """Test coordinator update failure."""
    # Mock list_scripts to raise an exception
    with patch.object(mock_coordinator, "list_scripts", side_effect=Exception("Network error")):
        with pytest.raises(UpdateFailed, match="Error communicating with device"):
            await mock_coordinator._async_update_data()


async def test_coordinator_update_with_status_exception(hass: HomeAssistant, mock_coordinator):
    """Test coordinator update with status exception."""
    with aioresponses() as m:
        m.get(
            "http://192.168.1.100/rpc/Script.List",
            payload={
                "scripts": [
                    {"id": 1, "name": "test1", "enable": True},
                ]
            },
        )
        # Status fails for script 1
        m.get("http://192.168.1.100/rpc/Script.GetStatus?id=1", exception=ConnectionError())

        data = await mock_coordinator._async_update_data()

        assert len(data["scripts"]) == 1
        # Script should have default values when status fails
        assert data["scripts"][0]["running"] is False
        assert data["scripts"][0]["mem_used"] == 0


# ===== WebSocket Tests =====


async def test_websocket_start(hass: HomeAssistant, mock_coordinator):
    """Test starting WebSocket listener."""
    with patch.object(mock_coordinator, "_websocket_listener", return_value=asyncio.Future()):
        await mock_coordinator.async_start_websocket()

        assert mock_coordinator._ws_task is not None


async def test_websocket_already_running(hass: HomeAssistant, mock_coordinator):
    """Test starting WebSocket when already running."""
    mock_coordinator._ws_task = MagicMock()

    await mock_coordinator.async_start_websocket()

    # Should not create a new task
    assert mock_coordinator._ws_task is not None


async def test_websocket_shutdown(hass: HomeAssistant, mock_coordinator):
    """Test shutting down WebSocket."""

    # Create a real asyncio task that we can cancel
    async def dummy_task():
        await asyncio.sleep(100)

    task = asyncio.create_task(dummy_task())
    mock_coordinator._ws_task = task

    mock_session = AsyncMock()
    mock_coordinator._ws_session = mock_session

    await mock_coordinator.async_shutdown()

    assert task.cancelled()
    mock_session.close.assert_called_once()


async def test_websocket_shutdown_without_session(hass: HomeAssistant, mock_coordinator):
    """Test shutting down WebSocket without active session."""

    # Create a real asyncio task
    async def dummy_task():
        await asyncio.sleep(100)

    task = asyncio.create_task(dummy_task())
    mock_coordinator._ws_task = task
    mock_coordinator._ws_session = None

    await mock_coordinator.async_shutdown()

    assert task.cancelled()


async def test_websocket_listener_reconnect(hass: HomeAssistant, mock_coordinator):
    """Test WebSocket reconnection logic."""
    mock_ws = MagicMock()
    mock_ws.__aenter__ = AsyncMock(return_value=mock_ws)
    mock_ws.__aexit__ = AsyncMock()

    # Simulate connection error then cancel
    async def mock_messages():
        yield MagicMock(type=WSMsgType.ERROR)

    mock_ws.__aiter__ = lambda self: mock_messages()

    with patch("aiohttp.ClientSession") as mock_session_class:
        mock_session = MagicMock()
        mock_session.ws_connect.return_value = mock_ws
        mock_session.close = AsyncMock()
        mock_session_class.return_value = mock_session

        # Start listener in background
        task = asyncio.create_task(mock_coordinator._websocket_listener())

        # Let it run briefly
        await asyncio.sleep(0.1)

        # Cancel the task
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
