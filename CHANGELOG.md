# Changelog

## [v0.5.0-beta] - 2026-02-22

### Added

- Full Options Flow: Create, Edit, Delete with automatic backups
- Rollback logic for failed uploads
- Automatic backup retention (max 10 per script)
- WebSocket for real-time updates
- Services: `upload_script`, `delete_script`, `list_scripts`

### Features

- **Multiline Script Editor** in Options Flow
- Script Count & Running Scripts sensors
- Start/Stop/Autostart switches per script
- WebSocket live updates

### Fixes

- **88% test coverage** with pytest
- Flake8/Black compliant
- Gen2-only warning

### HACS-ready

- Custom Repository configured
- Brands Repo PR to follow

## [v0.1.0] - 2026-02-10 (Alpha)

- Initial Shelly Script Integration
