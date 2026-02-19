# custom_components\shabman\helpers.py

"""shABman Helper Functions."""

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


def register_icon(hass: HomeAssistant, icon_filename: str = "icon.png") -> bool:
    """Register shABman icon - sync, HA 2021-2026 kompatibel."""

    if hass.http is None:
        _LOGGER.debug("Icon registration skipped (test env)")
        return False

    possible_paths = [
        Path("/config/custom_components/shabman") / icon_filename,
        Path("/homeassistant/custom_components/shabman") / icon_filename,
        Path(hass.config.path("custom_components")) / "shabman" / icon_filename,
    ]

    icon_path = next((p for p in possible_paths if p.exists()), None)

    if not icon_path:
        _LOGGER.warning(f"shABman {icon_filename} missing")
        return False

    try:
        # Einfache SYNC API - funktioniert überall
        hass.http.register_static_path("/api/shabman/icon", str(icon_path), cache_seconds=3600)
        _LOGGER.info(f"shABman icon registered: {icon_path}")
        return True
    except Exception as err:
        _LOGGER.error(f"Icon registration failed: {err}")
        return False
