# custom_components\shabman\helpers.py

"""shABman Helper Functions."""

import logging
from pathlib import Path

from homeassistant.core import HomeAssistant

try:
    from homeassistant.components.http import StaticPathConfig  # HA 2025.7+

    HAS_NEW_API = True
except ImportError:
    HAS_NEW_API = False

_LOGGER = logging.getLogger(__name__)


async def async_register_icon(hass: HomeAssistant, icon_filename: str = "icon.png") -> bool:
    """Register shABman icon - HA 2021-2026."""

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
        if HAS_NEW_API:
            # HA 2025.7+ async API
            await hass.http.async_register_static_paths(
                [
                    StaticPathConfig(
                        path="/api/shabman/icon",
                        local_file=str(icon_path),
                        cache_headers=True,  # 3600s
                    )
                ]
            )
            _LOGGER.info(f"Icon registered (new API): {icon_path}")
        else:
            # Alt (deprecated, aber funktioniert)
            hass.http.register_static_path("/api/shabman/icon", str(icon_path), cache_seconds=3600)
            _LOGGER.info(f"Icon registered (old API): {icon_path}")
        return True
    except Exception as err:
        _LOGGER.error(f"Icon registration failed: {err}")
        return False
