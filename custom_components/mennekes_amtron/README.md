# Mennekes AMTRON Wallbox Integration for Home Assistant

Complete Home Assistant integration for Mennekes AMTRON 4Business 730 Charging Wallbox with real-time monitoring, charging history, and full control.

## 🚀 Features

### Sensors (34+)
- **Voltages**: L1, L2, L3 (V)
- **Currents**: L1, L2, L3 (A)
- **Power**: L1, L2, L3, Total (W)
- **Energy**: Per phase, total, session (kWh)
- **Status**: Charging state, vehicle state, CP status
- **Control**: HEMS limit, safe current, phase mode
- **History**: Total sessions, total cost, last vehicle

### Entities
- **Sensors**: Real-time meter data via Modbus TCP
- **Numbers**: HEMS Current Limit, Safe Current (adjustable)
- **Switches**: Charging control, phase switching
- **Templates**: Energy cost, session tracking

### Dashboards
- **wallbox-main**: Real-time monitoring (voltage, current, power, energy)
- **wallbox-history**: Charging history (sessions, vehicles, costs)
- **wallbox-systemlogs**: System events and logs
- **wallbox-config**: Configuration and settings

## 📦 Installation

### Option 1: HACS (Recommended) ⭐

1. **Open HACS** in Home Assistant
2. **Repositories** → **Custom repositories**
3. Add: `https://github.com/nobelp/mennekes-amtron-ha`
4. Search **"Mennekes AMTRON"**
5. Click **Install**
6. **Restart Home Assistant**
7. Settings → Devices & Services → **[CREATE INTEGRATION](#configuration)**

### Option 2: Manual

```bash
cd /config/custom_components
git clone https://github.com/nobelp/mennekes-amtron-ha mennekes_amtron
# Restart Home Assistant
```

## ⚙️ Configuration

### Via UI (Recommended)

1. Settings → Devices & Services
2. **Create Integration** → Search "Mennekes AMTRON"
3. Enter configuration:
   - **Host**: `192.168.2.179` (wallbox IP)
   - **Modbus Port**: `502` (default)
   - **API Password**: Wallbox installer password
   - **Scan Interval**: `30` seconds
   - **Electricity Price**: `0.29` CHF/kWh

### Additional YAML Configuration (Optional)

Add to your `configuration.yaml`:

```yaml
# Automations (session tracking, notifications)
automation: !include custom_components/mennekes_amtron/automations_wallbox.yaml

# Template sensors (cost calculation, derived values)
template: !include custom_components/mennekes_amtron/template_sensors_wallbox.yaml

# Input helpers (vehicle names, RFID tags)
input_text: !include_dir_merge_named custom_components/mennekes_amtron/input_wallbox.yaml

# Alternative: Native Modbus (if issues with coordinator)
modbus: !include custom_components/mennekes_amtron/modbus_wallbox.yaml
```

### Alternative: Native Modbus Integration

If you prefer Home Assistant's built-in Modbus support:

```yaml
# configuration.yaml
modbus: !include custom_components/mennekes_amtron/modbus_wallbox.yaml
```

This provides 60+ meter registers directly via Modbus (no custom component needed).

## 📊 Dashboards

Beautiful pre-built dashboards for wallbox monitoring and control!

### Available Dashboards

- **wallbox_dashboard.yaml** - Main realtime monitoring (voltage, current, power, energy)
- **wallbox_dashboard.json** - Alternative JSON format

### Import Dashboards to Home Assistant

#### Method 1: Automatic via YAML (Recommended)

Add to your `configuration.yaml`:

```yaml
# Dashboards
homeassistant:
  packages:
    mennekes_wallbox_dashboards: !include custom_components/mennekes_amtron/wallbox_dashboard.yaml
```

Then restart Home Assistant. Dashboards appear automatically in UI.

#### Method 2: Manual Import via UI

1. Open Home Assistant
2. Settings → Dashboards (left sidebar)
3. **Create Dashboard** → Give it a name (e.g., "Wallbox")
4. Click **Edit Dashboard** (pencil icon)
5. Click **⋮** (three dots) → **Edit dashboard details** → **Raw configuration editor**
6. Delete the default content
7. Copy-paste content from `custom_components/mennekes_amtron/wallbox_dashboard.yaml`
8. Click **Save**

#### Method 3: File-based Setup

1. Create `/config/dashboards/` directory (if not exists)
2. Copy `wallbox_dashboard.yaml` to `/config/dashboards/wallbox.yaml`
3. In Home Assistant:
   - Settings → Dashboards
   - New dashboard appears automatically
   - Customize as needed

#### Method 4: Using setup.sh Script (Automatic)

```bash
cd /config/custom_components/mennekes_amtron
chmod +x setup.sh
./setup.sh
```

This automatically:
- Creates dashboard directory
- Imports dashboard files
- Configures automations
- Adds input helpers
- Restarts Home Assistant

## 🛠️ Troubleshooting

### "Modbus communication error: Not connected"

1. **Verify wallbox is reachable**:
   ```bash
   ping 192.168.2.179
   nc -zv 192.168.2.179 502
   ```

2. **Check wallbox settings**:
   - Modbus TCP enabled? (Wallbox Settings → Modbus)
   - Correct IP & port? (192.168.2.179:502)
   - Wallbox powered on?

3. **Check HA logs**:
   - Settings → System → Logs
   - Filter: `mennekes`
   - Look for connection errors

4. **Try native Modbus** (alternative):
   - Use `modbus_wallbox.yaml` instead of custom component
   - Built-in Modbus is sometimes more stable

### Sensors are empty

- Check Modbus connection (see above)
- Verify wallbox responds to Modbus requests
- Check configuration: host, port, password correct?

### High power values

- Power is in Watts (not kW)
- Energy is in kWh
- Current is in Ampere (not mA)

## 📋 Architecture

- **ModbusDataCoordinator**: Modbus TCP polling (meter data)
- **SessionDataCoordinator**: HTTP API (charging history)
- **34+ Sensor Entities**: Real-time values + history
- **Control Entities**: Number, Switch for manual control

## 📚 Files

- `coordinator.py` - Modbus + API data polling
- `sensor.py` - All 34+ sensor entities
- `number.py` - Adjustable controls (HEMS, current)
- `switch.py` - Binary controls (charging, phases)
- `config_flow.py` - UI setup wizard
- `strings.json` - UI labels & help text
- `modbus_wallbox.yaml` - Native Modbus config (alternative)
- `automations_wallbox.yaml` - Session tracking automations
- `template_sensors_wallbox.yaml` - Derived values (cost, duration)
- `input_wallbox.yaml` - User inputs (RFID, vehicle names)
- `wallbox_dashboard.yaml` - Lovelace dashboard

## 🚀 Quick Start (5 minutes)

1. **Install via HACS**
   - HACS → Custom repositories → Add `https://github.com/nobelp/mennekes-amtron-ha`
   - Search "Mennekes AMTRON" → Install
   - Restart Home Assistant

2. **Create Integration**
   - Settings → Devices & Services → Create Integration
   - Search "Mennekes AMTRON"
   - Enter: host=192.168.2.179, port=502, password

3. **Add Dashboards** (Optional but recommended)
   - Settings → Dashboards
   - Create Dashboard "Wallbox"
   - Edit → Raw config → Copy from `wallbox_dashboard.yaml`
   - Save

4. **Done!** 🎉
   - 34+ sensors with live data
   - Beautiful dashboard
   - Full control

## 📖 Documentation

- [INSTALL.md](INSTALL.md) - Detailed installation guide
- [Home Assistant Docs](https://www.home-assistant.io/)
- [Mennekes AMTRON Docs](https://www.mennekes.de/)

## 🔗 Links

- **GitHub**: https://github.com/nobelp/mennekes-amtron-ha
- **Issues**: https://github.com/nobelp/mennekes-amtron-ha/issues
- **HACS**: https://hacs.xyz/

## 📝 Changelog

- **v2.0.0** - Complete stable release with dashboards & automations
- **v1.7.4** - Real coordinator from production HA
- **v1.7.0** - Full 34+ sensor integration
- **v1.6.x** - Initial release

## 📄 License

MIT

---

**Questions?** Open an [issue](https://github.com/nobelp/mennekes-amtron-ha/issues) on GitHub!
