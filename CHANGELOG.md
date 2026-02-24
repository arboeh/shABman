# Changelog

## [v0.5.1-beta] - 2026-02-24

### Added

- **Security hardening**: Minimal GitHub Actions permissions (`contents: read`)
- **Backup improvement**: Device IP included in backup filenames (`script_192-168-1-100_1_edit_20260224_1830.json`)
- **Extended tests**: Additional test coverage for backup filename logic

### Changes

- `actions/setup-python@v6` & `actions/checkout@v6` (future-proof)
- `actions/checkout@v6` with `fetch-depth: 2` for improved CI performance

### Fixes

- CI workflow security warnings resolved

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
