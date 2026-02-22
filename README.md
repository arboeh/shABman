<img src="images/logo.svg" alt="jaABlu" height="40"/>

🇬🇧 English | [🇩🇪 **Deutsch**](README.de.md)

## Shelly Script Manager for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant)](https://www.home-assistant.io/)
[![release](https://img.shields.io/github/v/release/arboeh/shABman?display_name=tag)](https://github.com/arboeh/shABman/releases/latest)
[![Tests](https://github.com/arboeh/shABman/workflows/Tests/badge.svg)](https://github.com/arboeh/shABman/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/arboeh/shABman/blob/main/LICENSE)
[![maintained](https://img.shields.io/maintenance/yes/2026)](https://github.com/arboeh/shABman/graphs/commit-activity)
[![Shelly](https://img.shields.io/badge/Shelly-Gen2%2FGen3-00A1DF?logo=shelly)](https://shelly.cloud)


> **⚠️ Beta Release** – shABman 0.5.0-beta is functional but under active development.
> Expect breaking changes before 1.0.0. Please report issues on GitHub.

**shABman** lets you manage [Shelly Gen2/Gen3](https://shelly.cloud) scripts directly
from Home Assistant – without leaving the UI.

## Features

- 📋 **List scripts** – all scripts on your device as HA entities
- ✏️ **Edit scripts** – modify name and code via the Options Flow UI
- 📤 **Create scripts** – upload new scripts with chunked transfer (up to 4 KB/chunk)
- 🗑️ **Delete scripts** – with automatic backup before deletion
- 🔄 **Rollback on failure** – if an edit upload fails, the original is restored automatically
- 💾 **Backup retention** – up to 10 backups per script in `config/shabman_backups/`
- ⚡ **Real-time updates** – WebSocket connection for instant status changes
- 🔘 **Switch entities** – start/stop scripts and toggle autostart per script
- 📊 **Sensor entities** – total script count and running script count
- 🛠️ **HA Services** – `upload_script`, `delete_script`, `list_scripts` for automations

## Requirements

- Home Assistant **2024.1+**
- Shelly **Gen2 or Gen3** device (e.g. Plus, Pro, Mini series)
- Device must be accessible via local IP (HTTP)

## Installation via HACS

1. Open HACS → **Integrations**
2. Click **⋮ → Custom repositories**
3. Add `https://github.com/arboeh/shABman` as type **Integration**
4. Search for **shABman** and install
5. Restart Home Assistant

## Manual Installation

1. Copy `custom_components/shabman/` to your `config/custom_components/` folder
2. Restart Home Assistant

## Setup

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for **shABman**
3. Enter the local IP address of your Shelly device
4. The device is validated and added automatically

## Usage

After setup, open the integration options via **Configure** to manage scripts:

| Option | Description |
|---|---|
| 📤 Create new script | Upload a new script by name and code |
| ✏️ Manage scripts | Select and edit an existing script |
| 🗑️ Delete script | Select and confirm deletion (backup created automatically) |

## Entities

For each script on the device, shABman creates:

| Entity | Type | Description |
|---|---|---|
| `switch.shelly_script_manager_status_<name>` | Switch | Start / Stop script |
| `switch.shelly_script_manager_autostart_<name>` | Switch | Enable / Disable autostart |
| `sensor.shelly_script_manager_script_count` | Sensor | Total number of scripts |
| `sensor.shelly_script_manager_running_scripts` | Sensor | Number of currently running scripts |

## Services

### `shabman.upload_script`
```yaml
service: shabman.upload_script
data:
  device_id: "shellyplus1pm-aabbccddeeff"
  name: "my_script"
  code: "print('Hello');"
```

### `shabman.delete_script`
```yaml
service: shabman.delete_script
data:
  device_id: "shellyplus1pm-aabbccddeeff"
  script_id: 1
```

### `shabman.list_scripts`
```yaml
service: shabman.list_scripts
data:
  device_id: "shellyplus1pm-aabbccddeeff"
```
Fires a `shabman_scripts_listed` event with the script list.

## Backups

Before every edit or delete, shABman saves the script code as a JSON file:

```
config/shabman_backups/script_1_delete_20260222_121500.json
```

A maximum of **10 backups per script** are kept (oldest deleted automatically).

## Known Limitations (0.5.0-beta)

- No authentication support for password-protected Shelly devices
- Firmware version not reflected in device info (shows static value)
- `iot_class` is set to `local_polling`; WebSocket push is used in addition but not exclusively

## Planned Features (future releases)

- 🔗 **GitHub Integration**
  Load and import scripts directly from GitHub repositories
- ✅ **Script Editor**
  Advanced editor with syntax validation and syntax highlighting
- 🔐 **Authentication**
  Support for password-protected Shelly devices
- 📱 **Mobile Optimization**
  Lovelace cards for script overview and management

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

## License

MIT – see [LICENSE](LICENSE).

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://hacs.xyz
[version-badge]: https://img.shields.io/badge/version-0.5.0--beta-blue.svg
[releases-url]: https://github.com/arboeh/shABman/releases
[license-badge]: https://img.shields.io/badge/License-MIT-yellow.svg
[license-url]: LICENSE
