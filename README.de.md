<img src="images/logo.svg" alt="jaABlu" height="40"/>

[🇬🇧 English](README.md) | 🇩🇪 **Deutsch**

## Shelly Script Manager für Home Assistant

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant)](https://www.home-assistant.io/)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![release](https://img.shields.io/github/v/release/arboeh/shABman?display_name=tag)](https://github.com/arboeh/shABman/releases/latest)
[![Tests](https://github.com/arboeh/shABman/workflows/Tests/badge.svg)](https://github.com/arboeh/shABman/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/arboeh/shABman/blob/main/LICENSE)
[![maintained](https://img.shields.io/maintenance/yes/2026)](https://github.com/arboeh/shABman/graphs/commit-activity)
[![Shelly](https://img.shields.io/badge/Shelly-Gen2%2FGen3-00A1DF?logo=shelly)](https://shelly.cloud)

> **⚠️ Beta-Version** – shABman 0.5.0-beta ist funktionsfähig, wird aber aktiv entwickelt.
> Erwarte Änderungen vor 1.0.0. Bitte melde Probleme auf GitHub.

**shABman** ermöglicht das Verwalten von [Shelly Gen2/Gen3](https://shelly.cloud)-Scripts direkt aus Home Assistant – ohne die UI zu verlassen.

## Funktionen

- 📋 **Scripts anzeigen** – alle Scripts als HA-Entities
- ✏️ **Scripts bearbeiten** – Name und Code über Options Flow
- 📤 **Neue Scripts erstellen** – Upload mit Chunking (bis 4 KB/Chunk)
- 🗑️ **Scripts löschen** – mit automatischer Sicherung vorher
- 🔄 **Rollback bei Fehlern** – bei fehlgeschlagenem Edit wird Original wiederhergestellt
- 💾 **Backup-Retention** – max. 10 Backups pro Script in `config/shabman_backups/`
- ⚡ **Echtzeit-Updates** – WebSocket für sofortige Statusänderungen
- 🔘 **Switch-Entities** – Start/Stop und Autostart pro Script
- 📊 **Sensor-Entities** – Gesamtanzahl und laufende Scripts
- 🛠️ **HA-Services** – `upload_script`, `delete_script`, `list_scripts`

## Voraussetzungen

- Home Assistant **2024.1+**
- Shelly **Gen2 oder Gen3** (Plus, Pro, Mini Serie)
- Gerät lokal per IP erreichbar (HTTP)

## Installation über HACS

1. HACS → **Integrationen**
2. **⋮ → Benutzerdefinierte Repositories**
3. `https://github.com/arboeh/shABman` als **Integration** hinzufügen
4. **shABman** suchen und installieren
5. HA neu starten

## Manuelle Installation

1. `custom_components/shabman/` in `config/custom_components/` kopieren
2. HA neu starten

## Einrichtung

1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. **shABman** suchen
3. Lokale IP-Adresse des Shelly-Geräts eingeben
4. Gerät wird validiert und automatisch hinzugefügt

## Bedienung

Nach Einrichtung über **Integration konfigurieren** Scripts verwalten:

| Option | Beschreibung |
|---|---|
| 📤 Neues Script erstellen | Neues Script per Name und Code hochladen |
| ✏️ Scripts verwalten | Script auswählen und bearbeiten |
| 🗑️ Script löschen | Script auswählen und bestätigen (Backup automatisch!) |


## Entities

Pro Script auf dem Gerät:

| Entity | Typ | Beschreibung |
|---|---|---|
| `switch.shelly_script_manager_status_<name>` | Schalter | Script starten/stoppen |
| `switch.shelly_script_manager_autostart_<name>` | Schalter | Autostart ein/aus |
| `sensor.shelly_script_manager_script_count` | Sensor | Anzahl aller Scripts |
| `sensor.shelly_script_manager_running_scripts` | Sensor | Anzahl laufender Scripts |

## Services

### `shabman.upload_script`
```yaml
service: shabman.upload_script
data:
  device_id: "shellyplus1pm-aabbccddeeff"
  name: "mein_script"
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
→ Event `shabman_scripts_listed` mit Script-Liste.

## Backups

Vor jedem Edit/Löschvorgang wird der Script-Code als JSON gesichert:

```
config/shabman_backups/script_1_delete_20260222_121500.json
```

**Max. 10 Backups pro Script** (älteste werden automatisch gelöscht).

## Bekannte Einschränkungen (0.5.0-beta)

- Keine Authentifizierung für passwortgeschützte Shelly-Geräte
- `iot_class` ist `local_polling`; WebSocket wird zusätzlich genutzt

## Geplante Features (zukünftige Versionen)

- 🔗 **GitHub-Integration**
  Scripts direkt aus GitHub-Repos laden und importieren
- ✅ **Script-Editor**
  Erweiterter Editor mit Syntax-Validierung und Syntax-Highlighting
- 🔐 **Authentifizierung**
  Passwortgeschützte Shelly-Geräte
- 📱 **Mobile-Optimierung**
  Lovelace-Cards für Script-Management

## Changelog

Siehe [CHANGELOG.md](CHANGELOG.md).

## Lizenz

MIT © [arboeh](https://github.com/arboeh) – see [LICENSE](LICENSE)

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://hacs.xyz
[version-badge]: https://img.shields.io/badge/version-0.5.0--beta-blue.svg
[releases-url]: https://github.com/arboeh/shABman/releases
[license-badge]: https://img.shields.io/badge/Lizenz-MIT-yellow.svg
[license-url]: LICENSE
