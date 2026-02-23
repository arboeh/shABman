<img src="images/logo.svg" alt="jaABlu" height="40"/>

[🇬🇧 English](README.md) | 🇩🇪 **Deutsch**

## Shelly Script Manager für Home Assistant

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5?logo=home-assistant)](https://www.home-assistant.io/)
[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://hacs.xyz)
[![release](https://img.shields.io/github/v/release/arboeh/shABman?display_name=tag)](https://github.com/arboeh/shABman/releases/latest)
[![codecov](https://codecov.io/gh/arboeh/shABman/branch/main/graph/badge.svg)](https://codecov.io/gh/arboeh/shABman)
[![CI](https://github.com/arboeh/shABman/workflows/CI/badge.svg)](https://github.com/arboeh/shABman/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/arboeh/shABman/blob/main/LICENSE)
[![maintained](https://img.shields.io/maintenance/yes/2026)](https://github.com/arboeh/shABman/graphs/commit-activity)
[![Shelly](https://img.shields.io/badge/Shelly-Gen2%2FGen3-00A1DF?logo=shelly)](https://shelly.cloud)

> **⚠️ Beta-Version** - shABman 0.5.0-beta ist funktionsfähig, wird aber aktiv entwickelt.
> Erwarte Änderungen vor 1.0.0. Bitte melde Probleme auf GitHub.

**shABman** ermöglicht das Verwalten von [Shelly Gen2/Gen3](https://shelly.cloud)-Scripts direkt aus Home Assistant - ohne die UI zu verlassen.

## Funktionen

- 📋 **Scripts anzeigen** - alle Scripts als HA-Entities
- ✏️ **Scripts bearbeiten** - Name und Code über Options Flow
- 📤 **Neue Scripts erstellen** - Upload mit Chunking (bis 4 KB/Chunk)
- 🗑️ **Scripts löschen** - mit automatischer Sicherung vorher
- 🔄 **Rollback bei Fehlern** - bei fehlgeschlagenem Edit wird Original wiederhergestellt
- 💾 **Backup-Retention** - max. 10 Backups pro Script in `config/shabman_backups/`
- ⚡ **Echtzeit-Updates** - WebSocket für sofortige Statusänderungen
- 🔘 **Switch-Entities** - Start/Stop und Autostart pro Script
- 📊 **Sensor-Entities** - Gesamtanzahl und laufende Scripts
- 🛠️ **HA-Services** - `upload_script`, `delete_script`, `list_scripts`
- **🧪 Umfangreiche Testabdeckung**
  - **88% Code Coverage** mit pytest + pytest-homeassistant-custom-component
  - Unit-Tests für **Config Flow, Coordinator, Entities, Services**
  - Gemockte HTTP/WebSocket mit `aioresponses`
  - CI-Tests für **Python 3.11** (3.12 wartet auf Plugin-Fix)

## Voraussetzungen

- Home Assistant **2024.1+**
- Shelly **Gen2 oder Gen3** Gerät (Firmware 1.4.0+)
- Gerät lokal per IP erreichbar (HTTP)

## Unterstützte Geräte

**RPC Script API** (`rpc/Script.*`) verfügbar auf **allen Gen2/Gen3** (Firmware 1.4.0+)

| Device                         | Model ID     | Firmware | Status         | Serie     |
| ------------------------------ | ------------ | -------- | -------------- | --------- |
| ✅ **Shelly BLU Gateway**      | `SNGW-BT01`  | 1.4.0+   | **Getestet**   | Gateway   |
| 🟡 **Shelly Plus 1**           | `SHPLG-1`    | 1.4.0+   | Nicht getestet | Plus      |
| 🟡 **Shelly Plus 1PM**         | `SHPLG-1PM`  | 1.4.0+   | Nicht getestet | Plus      |
| 🟡 **Shelly Plus 1PM Mini G2** | `SHPLG-1M`   | 1.4.0+   | Nicht getestet | Plus Mini |
| 🟡 **Shelly Plus 2PM**         | `SHPLG-2PM`  | 1.4.0+   | Nicht getestet | Plus      |
| 🟡 **Shelly Plus Plug S**      | `SHPLG-IS`   | 1.4.0+   | Nicht getestet | Plus      |
| 🟡 **Shelly Plus Wall Outlet** | `SHPLG-WO`   | 1.4.0+   | Nicht getestet | Plus      |
| 🟡 **Shelly Pro 1**            | `SHPR-1`     | 1.4.0+   | Nicht getestet | Pro       |
| 🟡 **Shelly Pro 1PM**          | `SHPR-1PM`   | 1.4.0+   | Nicht getestet | Pro       |
| 🟡 **Shelly Pro 2**            | `SHPR-2`     | 1.4.0+   | Nicht getestet | Pro       |
| 🟡 **Shelly Pro 2PM**          | `SHPR-2PM`   | 1.4.0+   | Nicht getestet | Pro       |
| 🟡 **Shelly Pro 4PM**          | `SHPR-4PM`   | 1.4.0+   | Nicht getestet | Pro       |
| 🟡 **Shelly 1 Mini Gen3**      | `SH1MG3`     | 1.6.0+   | Nicht getestet | Gen3      |
| 🟡 **Shelly 1PM Mini Gen3**    | `SH1PMMG3`   | 1.6.0+   | Nicht getestet | Gen3      |
| 🟡 **Shelly 2PM Mini Gen3**    | `SH2PMMG3`   | 1.6.0+   | Nicht getestet | Gen3      |
| 🟡 **Shelly 2PM Gen3**         | `SH2PMG3`    | 1.6.0+   | Nicht getestet | Gen3      |
| 🟡 **Shelly Dimmer Gen3**      | `SHDMG3`     | 1.6.0+   | Nicht getestet | Gen3      |
| 🟡 **Shelly H&T Gen3**         | `SHHTG3`     | 1.6.0+   | Nicht getestet | Gen3      |
| 🟡 **Shelly Wall Display**     | `SHWSD`      | 1.4.0+   | Nicht getestet | Plus      |
| 🟡 **Shelly Motion 2**         | `SHBLUWG342` | 1.4.0+   | Nicht getestet | Battery   |
| 🟡 **Shelly Button 1**         | `SHBTN1`     | 1.4.0+   | Nicht getestet | Battery   |

> **✅ Getestet**<br>
> **🟡 Nicht getestet**: RPC API vorhanden, Community-Tests erwünscht<br>
> **Model ID** abrufen: `http://[IP]/rpc/Shelly.GetDeviceInfo`<br>
> **[Gerät fehlt? Issue erstellen](https://github.com/arboeh/shABman/issues/new)**

## Screenshots

### ![Marke](images/select_brand.png)<br>

**Markenerkennung**<br>
shABman erscheint in Geräteliste

### ![Setup](images/setup.png)<br>

**Einrichtung**<br>
Shelly Geräte-IP eingeben → automatische Validierung

### ![Gerät erstellt](images/device_created.png)<br>

**Integration bereit**<br>
Entities werden automatisch erstellt

### ![Übersicht](images/device_overview.png)<br>

**Geräteübersicht**<br>
Sensoren für Script-Anzahl + laufende Scripts

### ![Script-Menü](images/menu.png)<br>

**Script Manager**<br>
Scripts erstellen, bearbeiten, löschen über UI

### ![Editor](images/editor.png)<br>

**Script Editor**<br>
Vollständiger Code-Editor mit Backup/Rollback

### ![Overview](images/sensor_overview.png)<br>

**Sensor Übersicht**<br>
Erstellte Sensoren und laufende Scripts

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

| Option                    | Beschreibung                                          |
| ------------------------- | ----------------------------------------------------- |
| 📤 Neues Script erstellen | Neues Script per Name und Code hochladen              |
| ✏️ Scripts verwalten      | Script auswählen und bearbeiten                       |
| 🗑️ Script löschen         | Script auswählen und bestätigen (Backup automatisch!) |

## Entities

Pro Script auf dem Gerät:

| Entity                                          | Typ      | Beschreibung             |
| ----------------------------------------------- | -------- | ------------------------ |
| `switch.shelly_script_manager_status_<name>`    | Schalter | Script starten/stoppen   |
| `switch.shelly_script_manager_autostart_<name>` | Schalter | Autostart ein/aus        |
| `sensor.shelly_script_manager_script_count`     | Sensor   | Anzahl aller Scripts     |
| `sensor.shelly_script_manager_running_scripts`  | Sensor   | Anzahl laufender Scripts |

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

MIT © 2026 [arboeh](https://github.com/arboeh) - see [LICENSE](LICENSE)

[hacs-badge]: https://img.shields.io/badge/HACS-Custom-orange.svg
[hacs-url]: https://hacs.xyz
[version-badge]: https://img.shields.io/badge/version-0.5.0--beta-blue.svg
[releases-url]: https://github.com/arboeh/shABman/releases
[license-badge]: https://img.shields.io/badge/Lizenz-MIT-yellow.svg
[license-url]: LICENSE
