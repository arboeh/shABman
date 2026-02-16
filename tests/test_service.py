# tests\test_service.py

"""Test the shABman services."""

from unittest.mock import patch

import pytest
from homeassistant.core import HomeAssistant

from custom_components.shabman.const import DOMAIN


async def test_service_upload_script(hass: HomeAssistant, setup_integration):
    """Test upload_script service."""
    entry = setup_integration

    # Debug: Print what we got
    print(f"Entry: {entry}")
    print(f"Entry type: {type(entry)}")

    # If entry is None, something is wrong with the fixture
    if entry is None:
        pytest.skip("setup_integration fixture returned None")

    # Check if entry exists in hass.data
    if entry.entry_id not in hass.data.get(DOMAIN, {}):
        pytest.skip(f"Entry {entry.entry_id} not found in hass.data[{DOMAIN}]")

    coordinator = hass.data[DOMAIN][entry.entry_id]

    with patch.object(coordinator, "upload_script", return_value=True) as mock_upload:
        await hass.services.async_call(
            DOMAIN,
            "upload_script",
            {
                "device_id": entry.data["device_id"],
                "name": "test_script",
                "code": "console.log('test');",
            },
            blocking=True,
        )
        await hass.async_block_till_done()

        mock_upload.assert_called_once_with("test_script", "console.log('test');")


async def test_service_delete_script(hass: HomeAssistant, setup_integration):
    """Test delete_script service."""
    entry = setup_integration

    if entry is None:
        pytest.skip("setup_integration fixture returned None")

    if entry.entry_id not in hass.data.get(DOMAIN, {}):
        pytest.skip(f"Entry {entry.entry_id} not found in hass.data[{DOMAIN}]")

    coordinator = hass.data[DOMAIN][entry.entry_id]

    with patch.object(coordinator, "delete_script", return_value=True) as mock_delete:
        await hass.services.async_call(
            DOMAIN,
            "delete_script",
            {
                "device_id": entry.data["device_id"],
                "script_id": 1,
            },
            blocking=True,
        )
        await hass.async_block_till_done()

        mock_delete.assert_called_once_with(1)


async def test_service_list_scripts(hass: HomeAssistant, setup_integration):
    """Test list_scripts service."""
    entry = setup_integration

    if entry is None:
        pytest.skip("setup_integration fixture returned None")

    await hass.services.async_call(
        DOMAIN,
        "list_scripts",
        {
            "device_id": entry.data["device_id"],
        },
        blocking=True,
    )
    await hass.async_block_till_done()
