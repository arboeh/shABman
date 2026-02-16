# tests/test_config_flow.py

"""Test the shABman config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

# Importiere die Exception direkt aus dem Modul
import custom_components.shabman.config_flow as config_flow
from custom_components.shabman.const import DOMAIN


async def test_form(hass: HomeAssistant) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] is None or result["errors"] == {}

    with patch(
        "custom_components.shabman.config_flow.validate_input",
        return_value={
            "title": "shellypluspm-test123",
            "device_type": "SNSW-001P16EU",
            "device_id": "shellypluspm-test123",
        },
    ), patch(
        "custom_components.shabman.async_setup_entry",
        return_value=True,
    ) as mock_setup_entry:
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "device_ip": "192.168.1.100",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "shellypluspm-test123"
    assert result2["data"] == {
        "device_ip": "192.168.1.100",
        "device_type": "SNSW-001P16EU",
        "device_id": "shellypluspm-test123",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(hass: HomeAssistant) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    with patch(
        "custom_components.shabman.config_flow.validate_input",
        side_effect=config_flow.CannotConnect,  # Verwende config_flow.CannotConnect
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "device_ip": "192.168.1.100",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}


async def test_form_already_configured(hass: HomeAssistant) -> None:
    """Test we abort if already configured."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={
            "device_ip": "192.168.1.100",
            "device_type": "SNSW-001P16EU",
            "device_id": "existing-device",
        },
        unique_id="existing-device",
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    with patch(
        "custom_components.shabman.config_flow.validate_input",
        return_value={
            "title": "existing-device",
            "device_type": "SNSW-001P16EU",
            "device_id": "existing-device",
        },
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                "device_ip": "192.168.1.100",
            },
        )

    assert result2["type"] == FlowResultType.ABORT
    assert result2["reason"] == "already_configured"
