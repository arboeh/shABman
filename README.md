# shABman - Shelly Script Manager für Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/arboeh/shabman.svg)](https://github.com/arboeh/shabman/releases)
[![License](https://img.shields.io/github/license/arboeh/shabman.svg)](LICENSE)

Eine Home Assistant Integration zur Verwaltung von Scripts auf Shelly Gen2/Gen3/Gen4 Geräten.

## 🎯 Features

- 📜 **Script-Verwaltung**: Anzeige aller Scripts auf Shelly-Geräten
- 🔗 **GitHub-Integration**: Verlinkung zu Script-Repositories
- 📁 **Gruppierung**: Organisation von Scripts nach Kategorien
- 🔄 **Installation**: Ein-Klick-Installation von Scripts auf Shelly-Geräte
- ✏️ **Editor**: Bearbeitung von Scripts direkt in Home Assistant (geplant für Phase 2)
- 🌐 **Multi-Device**: Unterstützung für alle Shelly Gen2+ Geräte

## 🔌 Unterstützte Geräte

### Shelly Plus Serie
- Shelly Plus 1, Plus 1PM, Plus 2PM
- Shelly Plus i4, Plus Plug S, Plus H&T

### Shelly Pro Serie
- Shelly Pro 1, Pro 1PM, Pro 2, Pro 2PM
- Shelly Pro 3, Pro 4PM, Pro EM

### Weitere
- Shelly Gen3 und Gen4 Geräte
- Shelly BLU Gateway

Alle Geräte müssen **Gen2 oder neuer** sein und Scripting unterstützen.

## 📦 Installation

### HACS (empfohlen)

1. Öffne HACS in Home Assistant
2. Gehe zu **Integrations**
3. Klicke auf die **drei Punkte** (⋮) oben rechts
4. Wähle **Custom repositories**
5. Füge diese URL hinzu: `https://github.com/arboeh/shabman`
6. Kategorie: **Integration**
7. Klicke auf **Add**
8. Suche nach "shABman" und installiere es
9. **Starte Home Assistant neu**

### Manuelle Installation

1. Lade die neueste Version von der [Releases-Seite](https://github.com/arboeh/shabman/releases) herunter
2. Entpacke das ZIP-Archiv
3. Kopiere den Ordner `custom_components/shabman` in dein `config/custom_components/` Verzeichnis
4. Starte Home Assistant neu

## ⚙️ Einrichtung

1. Gehe zu **Einstellungen** → **Geräte & Dienste**
2. Klicke auf **+ Integration hinzufügen**
3. Suche nach **"shABman"**
4. Gib die **IP-Adresse** deines Shelly-Geräts ein
5. Klicke auf **Absenden**

Die Integration erkennt automatisch, ob dein Gerät Scripting unterstützt.

## 🚀 Verwendung

Nach der Einrichtung findest du shABman in der Sidebar. Dort kannst du:

- ✅ Alle Scripts auf deinen Shelly-Geräten anzeigen
- 📂 Scripts gruppiert nach Kategorien durchsuchen
- 🔍 Details zu Scripts aufklappen und ansehen
- 🔘 Scripts per Toggle aktivieren/deaktivieren
- 📥 Scripts von GitHub auf dein Gerät installieren

## 🗺️ Roadmap

### Phase 1 (aktuell in Entwicklung)
- [x] Basis-Integration mit Config Flow
- [x] Shelly RPC API Integration
- [x] Script-Auflistung via Coordinator
- [ ] Frontend Panel mit UI
- [ ] GitHub-Script-Repository
- [ ] Script-Installation per Button

### Phase 2 (geplant)
- [ ] Script-Editor in der UI
- [ ] Lokale Persistierung editierter Scripts
- [ ] Script-Versionierung
- [ ] Backup/Restore Funktionalität
- [ ] Multi-Device Management

## 🛠️ Entwicklung

### Voraussetzungen
- Python 3.11 oder höher
- Home Assistant Core Development Environment
- Git
- Visual Studio Code (empfohlen)

### Lokales Setup

```bash
# Repository klonen
git clone https://github.com/arboeh/shabman.git
cd shabman

# In Home Assistant config kopieren (für Tests)
# Windows:
xcopy /E /I custom_components\shabman C:\path	o\homeassistant\config\custom_components\shabman

# Linux/Mac:
cp -r custom_components/shabman /path/to/homeassistant/config/custom_components/
```

### Testing

```bash
# Home Assistant neu starten
# Integration über UI hinzufügen
# Logs prüfen: config/home-assistant.log
```

## 🤝 Beitragen

Contributions sind herzlich willkommen! Bitte lies [CONTRIBUTING.md](CONTRIBUTING.md) für Details.

### Quick Start für Contributors

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Änderungen (`git commit -m 'feat: add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request gegen `dev`

## 📄 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe [LICENSE](LICENSE) für Details.

## 🙏 Credits

- Entwickelt mit ❤️ für die Home Assistant Community
- Basierend auf der [Shelly Gen2 API](https://shelly-api-docs.shelly.cloud/gen2/)
- Inspiriert durch die großartige Arbeit der Home Assistant Entwickler

## 💬 Support

- 🐛 [GitHub Issues](https://github.com/arboeh/shabman/issues) für Bugs und Feature Requests
- 💭 [Discussions](https://github.com/arboeh/shabman/discussions) für Fragen und Ideen
- 🏠 [Home Assistant Community Forum](https://community.home-assistant.io/)

## ⚠️ Haftungsausschluss

Diese Integration ist nicht offiziell von Allterco Robotics (Shelly) oder Home Assistant. Nutze sie auf eigene Verantwortung.

---

**Hinweis**: Dieses Projekt befindet sich in aktiver Entwicklung. Features können sich ändern.
