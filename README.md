# Mennekes AMTRON Wallbox Integration for Home Assistant

HACS-compatible Custom Integration for Mennekes AMTRON 4Business 730 Charging Wallbox.

## Features

- **34+ Sensors** for real-time monitoring:
  - Voltages (L1, L2, L3)
  - Currents (L1, L2, L3) in Ampere
  - Power (L1, L2, L3, Total) in Watt
  - Energy (L1, L2, L3, Total, Session) in kWh
  - Charging Status & Vehicle State
  - HEMS Control & DLM Settings

- **Control Entities** (number & switch):
  - HEMS Current Limit
  - Safe Current
  - Phase Switch Mode Control
  - Charging Control

- **Dual Data Sources**:
  - ModbusDataCoordinator: Real-time meter data via Modbus TCP
  - SessionDataCoordinator: Historical charging data via HTTP API

## Installation

### Option 1: HACS (Recommended)

1. Open Home Assistant → Settings → Devices & Services → **Custom repositories**
2. Add: `https://github.com/nobelp/mennekes-amtron-ha`
3. Search for **Mennekes AMTRON** → Install
4. Restart Home Assistant
5. Settings → Devices & Services → **Create Integration** → Search "Mennekes AMTRON"

### Option 2: Manual

```bash
cd /config/custom_components
git clone https://github.com/nobelp/mennekes-amtron-ha mennekes_amtron
# Restart Home Assistant
```

## Configuration

### Via UI (Config Flow)

1. Settings → Devices & Services → **Create Integration**
2. Search **"Mennekes AMTRON Wallbox"**
3. Enter:
   - **Host**: `192.168.2.179` (wallbox IP)
   - **Modbus Port**: `502` (default)
   - **API Password**: Wallbox installer password
   - **Scan Interval**: `30` seconds (Modbus polling)
   - **Electricity Price**: `0.29` CHF/kWh (for cost calculation)

### Alternative: Native Modbus Integration

If you prefer Home Assistant's built-in Modbus support:

```yaml
# configuration.yaml
modbus: !include modbus_wallbox.yaml
```

See `modbus_wallbox.yaml` in this repo for 60+ meter registers.

## Requirements

- Home Assistant 2026.1.0+
- pymodbus >= 3.6.0
- Wallbox with Modbus TCP enabled (port 502)

## Troubleshooting

### "Modbus communication error: Not connected"

1. **Verify connectivity**:
   ```bash
   ping 192.168.2.179
   nc -zv 192.168.2.179 502
   ```

2. **Check wallbox**:
   - Modbus enabled? (Settings → Modbus)
   - Correct IP & port? (192.168.2.179:502)
   - Powered on?

3. **Check HA logs**:
   - Settings → System → Logs
   - Filter: `mennekes`

## Architecture

- `coordinator.py` - Modbus TCP polling + session API
- `sensor.py` - 34+ sensor entities
- `number.py` - HEMS control
- `switch.py` - Charging control
- `config_flow.py` - UI setup
- `manifest.json` - Integration metadata

## Changelog

- **v1.7.2** - Fixed pymodbus slave parameter
- **v1.7.1** - Modbus compatibility improvements
- **v1.7.0** - Full restoration (34+ sensors, dual coordinators)
- **v1.6.3** - Correct scaling (A, kWh)

## Support

GitHub: https://github.com/nobelp/mennekes-amtron-ha
