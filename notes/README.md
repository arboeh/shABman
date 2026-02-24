# Release Checklist

Interne Anleitung zum Erstellen von **Development-Releases** und **öffentlichen HACS-Releases** für shABman.

## Repository-Setup

### Single Repo mit Branches

```
shABman/
├── main        # 🌟 Production Releases (git tag v0.5.0)
├── dev         # 🔧 Development & Beta-Releases (git tag v0.5.1-dev)
└── Remote: origin → https://github.com/arboeh/shABman
```

**Workflow:**

1. **Development** auf `dev` Branch
2. **Beta-Releases** → `dev` → `git tag v0.5.1-dev`
3. **Production** → Merge `dev → main` → `git tag v0.5.1`

---

## Voraussetzungen

- [ ] Virtual Environment: `uv sync --extra test`
- [ ] Tests: `.\scripts\test-local.ps1` ✅ **88%+ Coverage**
- [ ] Pre-commit: `pre-commit run --all-files` ✅ **passed**
- [ ] VS Code: `even-better-toml` + `ruff`
- [ ] `scripts/sync-manifest.ps1` funktioniert !!!! NOCH NICHT IMPLEMENTIERT !!!!

### Remote Setup (einmalig)

```powershell
git remote -v  # Sollte origin → GitHub zeigen
```

---

## Release Workflow

### 1. Development abschließen (dev Branch)

```powershell
git checkout dev
uv sync --extra test
```

### 2. Pre-commit Hooks ausführen

```powershell
pre-commit run --all-files
```

**Prüft automatisch:**

- ✅ Ruff Linting & Formatting
- ✅ Trailing Whitespace
- ✅ End-of-File Fixer
- ✅ JSON/YAML Syntax
- ✅ Merge Conflicts

### 3. Version aktualisieren

#### Single Source of Truth

```toml
# pyproject.toml
[project]
version = "0.5.1-dev"  # ← Development/Beta
# oder
version = "0.5.1"      # ← Production
```

#### Automatische Synchronisation

```powershell
# VS Code: Strg+S → even-better-toml formatiert automatisch
taplo format pyproject.toml
.\scripts\sync-manifest.ps1
```

**Aktualisiert:** `custom_components/shabman/manifest.json`

### 4. Tests ausführen

```powershell
.\scripts\test-local.ps1
```

**Erwartung:**

```
TOTAL    751     81    89%
Results: 83 passed, 0 failed
```

### 5. CHANGELOG.md aktualisieren

```markdown
## [v0.5.1-dev] - 2026-02-24

### Added

- Backup-Dateinamen mit Device-IP
- Retention-Logik nach Schreiben

### Fixed

- Test Coverage: options_flow.py 99%
```

### 6. Commit im dev-Branch

```powershell
git add .
git commit -m "feat: v0.5.1-dev (Backup IP + Retention Fix)"
git push origin dev
```

---

## Development Release (Beta)

### 7. Dev-Tag erstellen

```powershell
git checkout dev
git tag v0.5.1-dev
git push origin v0.5.1-dev
```

### 8. GitHub Release (Draft)

```
GitHub → Releases → Draft new release
├── Tag: v0.5.1-dev
├── Branch: dev
├── Title: shABman v0.5.1-dev
└── Notes: Copy aus CHANGELOG.md
```

**Status:** **Draft** (für Beta-Tester)

---

## Production Release

### 9. Merge dev → main

```powershell
git checkout main
git pull origin main
git merge dev --no-ff -m "Release v0.5.1: Backup & Retention"
```

### 10. Finale Checks

```powershell
pre-commit run --all-files
.\scripts\test-local.ps1
.\scripts\sync-manifest.ps1
```

### 11. Production Tag

```powershell
git tag -a v0.5.1 -m "shABman v0.5.1

### Added
- Backup-Dateinamen mit Device-IP
- Retention nach Schreiben (>10)
### Fixed
- Test Coverage 89%"
git push origin main --tags
```

### 12. GitHub Release (Public)

```
GitHub → Releases → v0.5.1 → Publish release
├── Copy Changelog
└── Assets: (optional) dist/*.zip
```

---

## Update-Testing (optional)

```powershell
# Vor Release in HA testen:
# 1. HACS → Custom Repository → shABman (dev Branch)
# 2. v0.5.1-dev installieren
# 3. Config backup → Update → Config restore prüfen
# 4. Backup-Funktion testen (Edit → Fail → Rollback)
```

---

## Troubleshooting

### Tests schlagen fehl

```powershell
Remove-Item -Recurse -Force .venv
uv sync --extra test
```

### Pre-commit Fehlermeldung

```powershell
pre-commit clean
pre-commit install
```

### manifest.json nicht synchron

```powershell
.\scripts\sync-manifest.ps1
```

### HACS zeigt alte Version

```
GitHub → Releases → Latest muss v0.5.1 sein
HACS → Reload → Update verfügbar
```

---

## Checkliste vor Release

**Kopiere in GitHub Issue:**

```markdown
## Release v0.5.1 Checklist

### Development (dev)

- [ ] `.\scripts\test-local.ps1` ✅ 89% Coverage
- [ ] `pre-commit run --all-files` ✅ passed
- [ ] `pyproject.toml` version = "0.5.1"
- [ ] `.\scripts\sync-manifest.ps1` ✅
- [ ] CHANGELOG.md aktualisiert
- [ ] `git push origin dev`

### Beta Release

- [ ] `git tag v0.5.1-dev`
- [ ] GitHub Release (Draft)

### Production (main)

- [ ] `git merge dev → main`
- [ ] Finale Tests ✅
- [ ] `git tag v0.5.1`
- [ ] `git push origin main --tags`
- [ ] GitHub Release (Published)

### HACS

- [ ] HACS zeigt Update (Restart erforderlich)
```

---

## Quick Reference

```powershell
# Development
git checkout dev
# ... develop ...
pre-commit run --all-files
git commit -m "feat: XYZ"
git push origin dev

# Beta Release
git tag v0.5.1-dev
git push origin v0.5.1-dev

# Production
git checkout main
git merge dev
git tag v0.5.1
git push origin main --tags
```

**Dauer:** Dev-Release **~3 Min**, Production **~7 Min** 🎉
