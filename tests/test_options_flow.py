# tests\test_options_flow.py

"""Tests for shABman options flow."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shabman.const import DOMAIN

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

MOCK_CONFIG = {
    "host": "192.168.1.100",
    "name": "Test Shelly",
}

MOCK_SCRIPTS = [
    {"id": 1, "name": "script_one", "enabled": True, "running": False},
    {"id": 2, "name": "script_two", "enabled": False, "running": True},
]


@pytest.fixture
def mock_coordinator():
    coordinator = MagicMock()
    coordinator.data = {"scripts": MOCK_SCRIPTS}
    coordinator.upload_script = AsyncMock(return_value=True)
    coordinator.delete_script = AsyncMock(return_value=True)
    coordinator.get_script_code = AsyncMock(return_value="// script code")
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


@pytest.fixture
async def setup_entry(hass, mock_coordinator):
    """Set up a config entry with mocked coordinator."""
    entry = MockConfigEntry(domain=DOMAIN, data=MOCK_CONFIG, entry_id="test_entry")
    entry.add_to_hass(hass)
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN]["test_entry"] = mock_coordinator
    return entry


# ---------------------------------------------------------------------------
# async_step_init
# ---------------------------------------------------------------------------


async def test_options_flow_init_shows_menu(hass, setup_entry):
    """Init step should show the main menu."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)

    assert result["type"] == "menu"
    assert result["step_id"] == "init"
    assert "create_script" in result["menu_options"]
    assert "manage_scripts" in result["menu_options"]
    assert "delete_script" in result["menu_options"]


# ---------------------------------------------------------------------------
# async_step_create_script
# ---------------------------------------------------------------------------


async def test_create_script_shows_form(hass, setup_entry):
    """Create script step should show a form when no input given."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_script"}
    )

    assert result["type"] == "form"
    assert result["step_id"] == "create_script"
    assert result["errors"] == {}


async def test_create_script_success(hass, setup_entry, mock_coordinator):
    """Create script should complete when upload succeeds."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_script"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"name": "new_script", "code": "print('hello')"},
    )

    assert result["type"] == "create_entry"
    mock_coordinator.upload_script.assert_called_once_with("new_script", "print('hello')")
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_create_script_upload_failed(hass, setup_entry, mock_coordinator):
    """Create script should show error when upload fails."""
    mock_coordinator.upload_script.return_value = False

    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "create_script"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"name": "new_script", "code": "print('hello')"},
    )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "upload_failed"}


# ---------------------------------------------------------------------------
# async_step_manage_scripts
# ---------------------------------------------------------------------------


async def test_manage_scripts_shows_form(hass, setup_entry):
    """Manage scripts step should show dropdown with available scripts."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "manage_scripts"}
    )

    assert result["type"] == "form"
    assert result["step_id"] == "manage_scripts"


async def test_manage_scripts_no_scripts_aborts(hass, setup_entry, mock_coordinator):
    """Manage scripts should abort when no scripts exist."""
    mock_coordinator.data = {"scripts": []}

    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "manage_scripts"}
    )

    assert result["type"] == "abort"
    assert result["reason"] == "no_scripts"


async def test_manage_scripts_select_proceeds_to_edit(hass, setup_entry, mock_coordinator):
    """Selecting a script should proceed to edit step."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "manage_scripts"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})

    assert result["type"] == "form"
    assert result["step_id"] == "edit_script"


# ---------------------------------------------------------------------------
# async_step_edit_script
# ---------------------------------------------------------------------------


async def test_edit_script_loads_code(hass, setup_entry, mock_coordinator):
    """Edit form should load script code via coordinator."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "manage_scripts"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})

    assert result["type"] == "form"
    assert result["step_id"] == "edit_script"
    mock_coordinator.get_script_code.assert_called_once_with(1)


async def test_edit_script_code_load_fails(hass, setup_entry, mock_coordinator):
    """Edit form should show fallback text when code cannot be loaded."""
    mock_coordinator.get_script_code.return_value = None

    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "manage_scripts"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})

    assert result["type"] == "form"
    # Fallback code is set, form still shown
    assert result["step_id"] == "edit_script"


async def test_edit_script_success(hass, setup_entry, mock_coordinator):
    """Successful edit should delete old script, upload new, refresh."""
    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await hass.config_entries.options.async_init(setup_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={"next_step_id": "manage_scripts"}
        )
        result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"name": "updated_script", "code": "// new code"},
        )

    assert result["type"] == "create_entry"
    mock_coordinator.delete_script.assert_called_once_with(1)
    mock_coordinator.upload_script.assert_called()


async def test_edit_script_delete_fails(hass, setup_entry, mock_coordinator):
    """When delete fails, edit form should show update_failed error."""
    mock_coordinator.delete_script.return_value = False

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await hass.config_entries.options.async_init(setup_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={"next_step_id": "manage_scripts"}
        )
        result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"name": "updated_script", "code": "// new code"},
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "update_failed"}


async def test_edit_script_upload_fails_rollback_succeeds(hass, setup_entry, mock_coordinator):
    """When upload fails but rollback succeeds, show update_failed_restored."""
    mock_coordinator.upload_script.side_effect = [False, True]  # fail, then rollback ok

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await hass.config_entries.options.async_init(setup_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={"next_step_id": "manage_scripts"}
        )
        result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"name": "updated_script", "code": "// new code"},
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "update_failed_restored"}


async def test_edit_script_upload_fails_rollback_fails(hass, setup_entry, mock_coordinator):
    """When upload and rollback both fail, show update_failed_lost."""
    mock_coordinator.upload_script.side_effect = [False, False]

    with patch("asyncio.sleep", new_callable=AsyncMock):
        result = await hass.config_entries.options.async_init(setup_entry.entry_id)
        result = await hass.config_entries.options.async_configure(
            result["flow_id"], user_input={"next_step_id": "manage_scripts"}
        )
        result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
        result = await hass.config_entries.options.async_configure(
            result["flow_id"],
            user_input={"name": "updated_script", "code": "// new code"},
        )

    assert result["type"] == "form"
    assert result["errors"] == {"base": "update_failed_lost"}


async def test_edit_script_not_found_aborts(hass, setup_entry, mock_coordinator):
    """Edit step should abort when script id is no longer in coordinator data."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "manage_scripts"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
    # Remove scripts from coordinator after selection
    mock_coordinator.data = {"scripts": []}
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={"name": "x", "code": "y"},
    )

    assert result["type"] == "abort"
    assert result["reason"] == "script_not_found"


# ---------------------------------------------------------------------------
# async_step_delete_script
# ---------------------------------------------------------------------------


async def test_delete_script_shows_form(hass, setup_entry):
    """Delete script step should show dropdown."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )

    assert result["type"] == "form"
    assert result["step_id"] == "delete_script"


async def test_delete_script_no_scripts_aborts(hass, setup_entry, mock_coordinator):
    """Delete script should abort when no scripts exist."""
    mock_coordinator.data = {"scripts": []}

    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )

    assert result["type"] == "abort"
    assert result["reason"] == "no_scripts"


async def test_delete_script_proceeds_to_confirm(hass, setup_entry):
    """Selecting a script for deletion should show confirm form."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})

    assert result["type"] == "form"
    assert result["step_id"] == "confirm_delete"


async def test_confirm_delete_always_creates_backup(hass, setup_entry, mock_coordinator):
    """Confirm delete form should trigger backup."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
    result = await hass.config_entries.options.async_configure(result["flow_id"])

    assert result["type"] == "form"
    # Prüfe delete-Aufruf statt exakte Anzahl
    assert any(mock_call[0] == "get_script_code" and mock_call[1][0] == 1 for mock_call in mock_coordinator.mock_calls)


# ---------------------------------------------------------------------------
# async_step_confirm_delete
# ---------------------------------------------------------------------------


async def test_confirm_delete_success(hass, setup_entry, mock_coordinator):
    """Confirmed deletion should call delete and return create_entry."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={})

    assert result["type"] == "create_entry"
    mock_coordinator.delete_script.assert_called_once_with(1)
    mock_coordinator.async_request_refresh.assert_called_once()


async def test_confirm_delete_fails_aborts(hass, setup_entry, mock_coordinator):
    """Failed deletion should abort with delete_failed reason."""
    mock_coordinator.delete_script.return_value = False

    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={})

    assert result["type"] == "abort"
    assert result["reason"] == "delete_failed"


async def test_confirm_delete_script_not_found(hass, setup_entry, mock_coordinator):
    """Confirm delete should abort if script disappears between steps."""
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
    mock_coordinator.data = {"scripts": []}
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={})

    assert result["type"] == "abort"
    assert result["reason"] == "script_not_found"


async def test_confirm_delete_submit_triggers_backup(hass, setup_entry, mock_coordinator):
    """Delete submit should trigger backup."""
    # Flow bis confirm_delete Form (ohne reset hier)
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={"next_step_id": "delete_script"}
    )
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={"script": "1"})
    result = await hass.config_entries.options.async_configure(result["flow_id"])  # Form

    # JETZT reset für isolierten Submit-Test
    mock_coordinator.get_script_code.reset_mock()

    # Submit (backup + delete)
    result = await hass.config_entries.options.async_configure(result["flow_id"], user_input={})

    assert result["type"] == "create_entry"
    mock_coordinator.get_script_code.assert_called_once_with(1)
