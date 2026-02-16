# tests/test_init.py

""" "Test the shABman component initialization."""

from homeassistant.core import HomeAssistant

from custom_components.shabman.const import DOMAIN


async def test_async_setup_entry(hass: HomeAssistant, setup_integration):
    """Test successful setup."""
    entry = setup_integration

    # Check that coordinator is loaded
    assert DOMAIN in hass.data
    assert entry.entry_id in hass.data[DOMAIN]

    coordinator = hass.data[DOMAIN][entry.entry_id]
    assert coordinator is not None

    # Check that services are registered
    assert hass.services.has_service(DOMAIN, "upload_script")
    assert hass.services.has_service(DOMAIN, "delete_script")
    assert hass.services.has_service(DOMAIN, "list_scripts")

    # Explicitly cancel websocket task before test ends
    if hasattr(coordinator, "_ws_task") and coordinator._ws_task:
        coordinator._ws_task.cancel()
        try:
            await coordinator._ws_task
        except Exception:
            pass

    await hass.async_block_till_done()
