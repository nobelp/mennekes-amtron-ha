# Changelog — Mennekes AMTRON Home Assistant Integration

Alle wichtigen Änderungen an diesem Projekt werden hier dokumentiert.

---

## [1.1.1] – 2026-07-15

### Added
- 🔧 **Modbus v1.5 Protocol Support** – Neue Custom Component Integration mit korrekten Register-Adressen
- 🆕 **Phase Switch Mode Sensor** – Unterstützung für dynamische Phasenumschaltung (11kW Geräte)
- 📊 **Corrected Meter Values** – Richtige int32 Register-Byte-Reihenfolge für exakte Energiemessung
- 🎁 **New HEMS v1.5 Support** – HEMS Current Limit mit 0.1A Schritte (Register 2000 statt 1000)

### Fixed
- 🐛 **Energy Calculation** – Korrekte Umrechnung von Wh zu kWh (int32 Byte-Reihenfolge)
- 🔌 **Register Mapping** – Voltage/Current/Power Register gemäß v1.5 Dokumentation (222-227 statt 200-202)
- 📋 **Session Data** – Korrigierte Register für Charged Energy (716 statt 705) und Charging Duration (718 statt 709)

### Changed
- 📝 **Documentation** – Entfernt: Home Assistant Quality Scale Kapitel
- 📚 **Sensor Documentation** – Ergänzt: Alle v1.5 Integration Sensoren mit genauen Registeradressen
- ⚡ **Deprecated Registers** – YAML Modbus liest nun nur noch v1.5 konforme Register

### Technical Details
- **Protocol Version**: 1.5 (AMTRON 4You500/4Business700)
- **Compatible Models**: 4You 400/500, 4Business 600/700 (identische Kommunikation)
- **Integration Type**: Custom Component (mennekes_amtron)
- **Breaking Changes**: Old modbus_wallbox.yaml deprecated; use custom component instead

---

## [1.1.0] – 2026-06-24

### Added
- 🎁 **HACS Official Support** – Vollständige HACS-Integration mit `hacs.json`
- 🔐 **Security Hardening** – Alle hardcoded IPs und Passwörter anonymisiert (192.x.x.x, MUSTER_PASSWORD)
- ✅ **GitHub Actions Workflows**:
  - HACS Validation (automatische Überprüfung)
  - YAML/JSON Linting
  - Security Checks (keine Secrets geleakt)
  - Version Validation
  - Release Automation
- 📚 **Enhanced Documentation**:
  - HACS Installation Guide
  - Home Assistant Quality Scale Assessment
  - Known Limitations & Supported Devices
  - Improved Troubleshooting Section
- 🔧 **Environment Variable Support** – Alle IPs und Passwörter via `.env` konfigurierbar
- 🏷️ **Version Badges** – GitHub Release, License, HACS Badges in README

### Changed
- 📝 **Anonymous Configuration** – IPs und Passwörter in Dokumentation durch Platzhalter ersetzt
- 📂 **.gitignore Update** – QUICKSTART.md, setup.sh, SYSTEMLOGS_SETUP.md, diagnose.sh sind nun versioniert (mit anonymisierten Inhalten)
- 🔄 **Improved Shell Scripts** – run_wallbox_fetch_logs.sh nutzt nun Umgebungsvariablen statt hardcoded Passwörter
- 📊 **Enhanced diagnose.sh** – Nutzt WALLBOX_URL Umgebungsvariable statt hardcoded IP

### Fixed
- 🔐 **Security Issue**: Echtes Installer-Passwort aus QUICKSTART.md, setup.sh und run_wallbox_fetch_logs.sh entfernt
- 🐛 **Dokumentation**: Alle hardcoded IPs durch generische Placeholder (192.x.x.x, 10.x.x.x) ersetzt
- 📋 **.env.example**: Verbesserte Struktur mit Kommentaren und Beispiel-Konfiguration

### Technical Details
- **Minimum Home Assistant Version**: 2026.1.0
- **Python Version**: 3.9+ (already included in HA)
- **Required HACS Cards**: apexcharts-card (2.2.3+)
- **Supported Wallbox**: Mennekes AMTRON 4Business 730 11 C2

---

## [1.0.5] – 2026-06-24

### Added
- Environment variable support for Wallbox API URLs (`WALLBOX_URL`)
- `.env.example` file with required configuration parameters
- Documentation for environment variable configuration

### Changed
- Hardcoded Wallbox API URLs replaced with environment variables in Python scripts
- Improved `.gitignore` with Home Assistant-specific files and temporary scripts

### Fixed
- Better security by externalizing IP addresses from source code

---

## [1.0.0] – 2026-06-24

### Initial Release

Complete Mennekes AMTRON Wallbox integration for Home Assistant:
- Real-time monitoring via Modbus TCP (Spannung, Strom, Leistung, Ladestatus)
- Charging sessions via REST API (history, vehicle mapping, costs)
- Control of HEMS limits, Safe Current, availability, charge interruption
- Dashboard with ApexCharts bar charts, monthly summary, session list
- Python automation scripts for data collection and processing

---

## Installation & Usage

### Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
# Edit .env with your Wallbox URL and password
```

### Running Scripts

```bash
# With environment variables
export WALLBOX_URL="http://192.x.x.x/api/v1"  # Replace 192.x.x.x with your Wallbox IP
export WALLBOX_PASS="MUSTER_PASSWORD"          # Replace with your installer password

python3 python_scripts/fetch_charging_sessions.py
python3 python_scripts/fetch_system_events.py
python3 python_scripts/fetch_system_logs.py
```

Or pass password as argument:
```bash
python3 python_scripts/fetch_charging_sessions.py your-installer-password
```

---

## Documentation

- `README.md` — Complete setup and architecture documentation
- `.env.example` — Environment variable reference
- `python_scripts/` — Individual Python script documentation in headers
