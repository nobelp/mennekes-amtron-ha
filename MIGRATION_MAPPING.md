# Mennekes AMTRON Wallbox - Migration Mapping to Home Assistant Custom Integration

**Date**: July 31, 2026  
**Current State**: YAML configs + Modbus TCP + REST API + Python scripts  
**Target**: Home Assistant Custom Integration with Python entity classes  
**Integration Domain**: `mennekes_amtron`  
**Integration Version**: 1.2.0-beta.1

---

## 1. MODBUS TCP REGISTERS

### Configuration
- **Connection Type**: TCP
- **Default Port**: 502
- **Slave ID**: 1
- **Input Type**: Holding (read-only)
- **Data Types**: uint16, uint32, string
- **Timeout**: 5 seconds
- **Retries**: 3
- **Retry on Empty**: true

### 1.1 System Information Registers (Read-Only Sensors)

| Hex Addr | Dec Addr | Register Name | Unique ID | Data Type | Unit | Device Class | State Class | Count | Entity Type | Notes |
|----------|----------|---|---|---|---|---|---|---|---|---|
| 0x64 | 100 | Firmware Version | `wallbox_firmware_version` | string | - | - | - | 2 | SensorEntity | 2-word string |
| 0x68 | 104 | OCPP CP Status | `wallbox_ocpp_cp_status` | uint16 | - | enum | - | 1 | SensorEntity | Status codes 0-9 |
| 0x69 | 105 | Error Codes 1 | `wallbox_error_codes_1` | uint32 | - | - | measurement | 1 | SensorEntity | Bitfield (16 bits) |
| 0x6B | 107 | Error Codes 2 | `wallbox_error_codes_2` | uint32 | - | - | measurement | 1 | SensorEntity | Bitfield |
| 0x6D | 109 | Error Codes 3 | `wallbox_error_codes_3` | uint32 | - | - | measurement | 1 | SensorEntity | Bitfield |
| 0x6F | 111 | Error Codes 4 | `wallbox_error_codes_4` | uint32 | - | - | measurement | 1 | SensorEntity | Bitfield |
| 0x78 | 120 | Protocol Version | `wallbox_protocol_version` | string | - | - | - | 2 | SensorEntity | 2-word string |
| 0x7A | 122 | Vehicle State | `wallbox_vehicle_state` | uint16 | - | enum | - | 1 | SensorEntity | States A-E |
| 0x7C | 124 | CP Availability | `wallbox_cp_availability` | uint16 | - | enum | - | 1 | SensorEntity | 0=unavailable, 1=available |
| 0x82 | 130 | Modbus Address Offset | `wallbox_modbus_address_offset` | uint16 | - | - | measurement | 1 | SensorEntity | - |
| 0x83 | 131 | Safe Current | `wallbox_safe_current` | uint16 | A | current | measurement | 1 | SensorEntity | Min: 0A, Max: 32A |
| 0x84 | 132 | Comm Timeout | `wallbox_comm_timeout` | uint16 | s | - | measurement | 1 | SensorEntity | Seconds |
| 0x86 | 134 | Operator Current Limit | `wallbox_operator_current_limit` | uint16 | A | current | measurement | 1 | SensorEntity | - |
| 0x8E | 142 | Chargepoint Model 1 | `wallbox_chargepoint_model_1` | string | - | - | - | 2 | SensorEntity | Part 1 of 5 |
| 0x90 | 144 | Chargepoint Model 2 | `wallbox_chargepoint_model_2` | string | - | - | - | 2 | SensorEntity | Part 2 of 5 |
| 0x92 | 146 | Chargepoint Model 3 | `wallbox_chargepoint_model_3` | string | - | - | - | 2 | SensorEntity | Part 3 of 5 |
| 0x94 | 148 | Chargepoint Model 4 | `wallbox_chargepoint_model_4` | string | - | - | - | 2 | SensorEntity | Part 4 of 5 |
| 0x96 | 150 | Chargepoint Model 5 | `wallbox_chargepoint_model_5` | string | - | - | - | 2 | SensorEntity | Part 5 of 5 |
| 0x98 | 152 | Plug Lock Status | `wallbox_plug_lock_status` | uint16 | - | - | measurement | 1 | SensorEntity | 0=unlocked, 1=locked |

### 1.2 Meter Values Registers (Read-Only Sensors)

| Hex Addr | Dec Addr | Register Name | Unique ID | Data Type | Unit | Device Class | State Class | Entity Type | Notes |
|----------|----------|---|---|---|---|---|---|---|---|
| 0xC8 | 200 | Meter Energy L1 | `wallbox_meter_energy_l1` | uint32 | Wh | energy | total_increasing | SensorEntity | 32-bit energy |
| 0xCA | 202 | Meter Energy L2 | `wallbox_meter_energy_l2` | uint32 | Wh | energy | total_increasing | SensorEntity | 32-bit energy |
| 0xCC | 204 | Meter Energy L3 | `wallbox_meter_energy_l3` | uint32 | Wh | energy | total_increasing | SensorEntity | 32-bit energy |
| 0xCE | 206 | Meter Power L1 | `wallbox_meter_power_l1` | uint32 | W | power | measurement | SensorEntity | - |
| 0xD0 | 208 | Meter Power L2 | `wallbox_meter_power_l2` | uint32 | W | power | measurement | SensorEntity | - |
| 0xD2 | 210 | Meter Power L3 | `wallbox_meter_power_l3` | uint32 | W | power | measurement | SensorEntity | - |
| 0xD4 | 212 | Meter Current L1 | `wallbox_meter_current_l1` | uint32 | mA | current | measurement | SensorEntity | In milliamps |
| 0xD6 | 214 | Meter Current L2 | `wallbox_meter_current_l2` | uint32 | mA | current | measurement | SensorEntity | In milliamps |
| 0xD8 | 216 | Meter Current L3 | `wallbox_meter_current_l3` | uint32 | mA | current | measurement | SensorEntity | In milliamps |
| 0xDA | 218 | Meter Total Energy | `wallbox_meter_total_energy` | uint32 | Wh | energy | total_increasing | SensorEntity | 32-bit total |
| 0xDC | 220 | Meter Total Power | `wallbox_meter_total_power` | uint32 | W | power | measurement | SensorEntity | Sum of 3 phases |
| 0xDE | 222 | Meter Voltage L1 | `wallbox_meter_voltage_l1` | uint32 | V | voltage | measurement | SensorEntity | - |
| 0xE0 | 224 | Meter Voltage L2 | `wallbox_meter_voltage_l2` | uint32 | V | voltage | measurement | SensorEntity | - |
| 0xE2 | 226 | Meter Voltage L3 | `wallbox_meter_voltage_l3` | uint32 | V | voltage | measurement | SensorEntity | - |

### 1.3 Dynamic Load Management (DLM) Registers (Read-Only Sensors)

| Hex Addr | Dec Addr | Register Name | Unique ID | Data Type | Unit | Device Class | State Class | Entity Type | Notes |
|----------|----------|---|---|---|---|---|---|---|---|
| 0x258 | 600 | DLM Mode | `wallbox_dlm_mode` | uint16 | - | enum | - | SensorEntity | Modes 0-4 |
| 0x262 | 610 | DLM EVSE Sub Dist Limit L1 | `wallbox_dlm_evse_sub_dist_limit_l1` | uint16 | A | current | measurement | SensorEntity | - |
| 0x263 | 611 | DLM EVSE Sub Dist Limit L2 | `wallbox_dlm_evse_sub_dist_limit_l2` | uint16 | A | current | measurement | SensorEntity | - |
| 0x264 | 612 | DLM EVSE Sub Dist Limit L3 | `wallbox_dlm_evse_sub_dist_limit_l3` | uint16 | A | current | measurement | SensorEntity | - |
| 0x265 | 613 | DLM Operator EVSE Sub Dist Limit L1 | `wallbox_dlm_operator_evse_sub_dist_limit_l1` | uint16 | A | current | measurement | SensorEntity | - |
| 0x266 | 614 | DLM Operator EVSE Sub Dist Limit L2 | `wallbox_dlm_operator_evse_sub_dist_limit_l2` | uint16 | A | current | measurement | SensorEntity | - |
| 0x267 | 615 | DLM Operator EVSE Sub Dist Limit L3 | `wallbox_dlm_operator_evse_sub_dist_limit_l3` | uint16 | A | current | measurement | SensorEntity | - |
| 0x26C | 620 | DLM External Meter Support | `wallbox_dlm_external_meter_support` | uint16 | - | - | measurement | SensorEntity | - |
| 0x26D | 621 | DLM Num Slaves Connected | `wallbox_dlm_num_slaves_connected` | uint16 | - | - | measurement | SensorEntity | - |
| 0x276 | 630 | DLM Overall Current Applied L1 | `wallbox_dlm_overall_current_applied_l1` | uint16 | A | current | measurement | SensorEntity | - |
| 0x277 | 631 | DLM Overall Current Applied L2 | `wallbox_dlm_overall_current_applied_l2` | uint16 | A | current | measurement | SensorEntity | - |
| 0x278 | 632 | DLM Overall Current Applied L3 | `wallbox_dlm_overall_current_applied_l3` | uint16 | A | current | measurement | SensorEntity | - |
| 0x279 | 633 | DLM Overall Current Available L1 | `wallbox_dlm_overall_current_available_l1` | uint16 | A | current | measurement | SensorEntity | - |
| 0x27A | 634 | DLM Overall Current Available L2 | `wallbox_dlm_overall_current_available_l2` | uint16 | A | current | measurement | SensorEntity | - |
| 0x27B | 635 | DLM Overall Current Available L3 | `wallbox_dlm_overall_current_available_l3` | uint16 | A | current | measurement | SensorEntity | - |

### 1.4 Charge Process Registers (Read-Only Sensors)

| Hex Addr | Dec Addr | Register Name | Unique ID | Data Type | Unit | Device Class | State Class | Entity Type | Notes |
|----------|----------|---|---|---|---|---|---|---|---|
| 0x2C1 | 705 | Charged Energy Session | `wallbox_charged_energy_session` | uint16 | Wh | energy | total_increasing | SensorEntity | 16-bit (capped ~64kWh) |
| 0x2C2 | 706 | Signaled Current | `wallbox_signaled_current` | uint16 | A | current | measurement | SensorEntity | - |
| 0x2C3 | 707 | Start Time | `wallbox_start_time` | uint32 | - | - | measurement | SensorEntity | UNIX timestamp |
| 0x2C5 | 709 | Charge Duration | `wallbox_charge_duration` | uint16 | s | - | measurement | SensorEntity | 16-bit seconds |
| 0x2C6 | 710 | End Time | `wallbox_end_time` | uint32 | - | - | measurement | SensorEntity | UNIX timestamp |
| 0x2C8 | 712 | Minimum Current Limit | `wallbox_minimum_current_limit` | uint16 | A | current | measurement | SensorEntity | - |
| 0x2CB | 715 | Max Current EV | `wallbox_max_current_ev` | uint16 | A | current | measurement | SensorEntity | - |
| 0x2CC | 716 | Charged Energy 32bit | `wallbox_charged_energy_32bit` | uint32 | Wh | energy | total_increasing | SensorEntity | 32-bit (larger capacity) |
| 0x2CE | 718 | Charge Duration 32bit | `wallbox_charge_duration_32bit` | uint32 | s | - | measurement | SensorEntity | 32-bit seconds |
| 0x2D0 | 720 | ID Tag 1 | `wallbox_id_tag_1` | string | - | - | - | SensorEntity | RFID tag (2-word string) |
| 0x2D2 | 722 | ID Tag 2 | `wallbox_id_tag_2` | string | - | - | - | SensorEntity | RFID tag (2-word string) |
| 0x2D4 | 724 | ID Tag 3 | `wallbox_id_tag_3` | string | - | - | - | SensorEntity | RFID tag (2-word string) |
| 0x2D6 | 726 | ID Tag 4 | `wallbox_id_tag_4` | string | - | - | - | SensorEntity | RFID tag (2-word string) |
| 0x2D8 | 728 | ID Tag 5 | `wallbox_id_tag_5` | string | - | - | - | SensorEntity | RFID tag (2-word string) |

### 1.5 HEMS Control Register (Read/Write - NumberEntity)

| Hex Addr | Dec Addr | Register Name | Unique ID | Data Type | Unit | Device Class | Min | Max | Step | Entity Type | Purpose |
|----------|----------|---|---|---|---|---|---|---|---|---|---|
| 0x3E8 | 1000 | HEMS Current Limit | `wallbox_hems_current_limit` | uint16 | A | current | 0 | 16 | 1 | NumberEntity | Dynamic load management |

**Total Modbus Registers**: 68 unique sensors + 1 writable number = 69 register addresses

---

## 2. TEMPLATE SENSORS (Computed/Derived Values)

### 2.1 Current Conversion Templates
Convert milliamps to amperes (divide by 1000, round to 2 decimals)

| Template Unique ID | Name | Unit | Device Class | State Class | Input Sensor | Formula | Entity Type |
|---|---|---|---|---|---|---|---|
| `wallbox_current_l1_ampere` | Wallbox Current L1 Ampere | A | current | measurement | `sensor.meter_current_l1` | mA / 1000 | SensorEntity |
| `wallbox_current_l2_ampere` | Wallbox Current L2 Ampere | A | current | measurement | `sensor.meter_current_l2` | mA / 1000 | SensorEntity |
| `wallbox_current_l3_ampere` | Wallbox Current L3 Ampere | A | current | measurement | `sensor.meter_current_l3` | mA / 1000 | SensorEntity |

### 2.2 Energy Conversion Templates
Convert Wh to kWh (divide by 1000, round to 2 decimals)

| Template Unique ID | Name | Unit | Device Class | State Class | Input Sensor | Formula | Entity Type |
|---|---|---|---|---|---|---|---|
| `wallbox_total_energy_kwh` | Wallbox Total Energy kWh | kWh | energy | total_increasing | `sensor.meter_total_energy` | Wh / 1000 | SensorEntity |
| `wallbox_energy_l1_kwh` | Wallbox Energy L1 kWh | kWh | energy | total_increasing | `sensor.meter_energy_l1` | Wh / 1000 | SensorEntity |
| `wallbox_energy_l2_kwh` | Wallbox Energy L2 kWh | kWh | energy | total_increasing | `sensor.meter_energy_l2` | Wh / 1000 | SensorEntity |
| `wallbox_energy_l3_kwh` | Wallbox Energy L3 kWh | kWh | energy | total_increasing | `sensor.meter_energy_l3` | Wh / 1000 | SensorEntity |
| `wallbox_session_energy_kwh` | Wallbox Session Energy kWh | kWh | energy | total_increasing | `sensor.charged_energy_32bit` | Wh / 1000 | SensorEntity |

### 2.3 Power Template
Pass-through with unit conversion

| Template Unique ID | Name | Unit | Device Class | State Class | Input Sensor | Entity Type |
|---|---|---|---|---|---|---|
| `wallbox_total_power` | Wallbox Total Power | W | power | measurement | `sensor.meter_total_power` | SensorEntity |

### 2.4 Time Formatting Template
Convert seconds to HH:MM:SS format

| Template Unique ID | Name | Input Sensor | Format | Entity Type | Notes |
|---|---|---|---|---|---|---|
| `wallbox_charge_duration_formatted` | Wallbox Charge Duration Formatted | `sensor.charge_duration_32bit` | HH:MM:SS | SensorEntity | Displays session duration |

### 2.5 Status Mapping Templates
Map numeric codes to human-readable text

| Template Unique ID | Name | Input Sensor | Mapping Type | Entity Type | Notes |
|---|---|---|---|---|---|
| `wallbox_cp_status_text` | Wallbox CP Status Text | `sensor.ocpp_cp_status` | OCPP Status (0-9) | SensorEntity | Charger status |
| `wallbox_charging_status` | Wallbox Charging Status | `sensor.ocpp_cp_status` | Simplified status | SensorEntity | With icon |
| `wallbox_vehicle_state_text` | Wallbox Vehicle State Text | `sensor.vehicle_state` | Vehicle states A-E | SensorEntity | SAE J1772 states |
| `wallbox_dlm_mode_text` | Wallbox DLM Mode Text | `sensor.dlm_mode` | DLM modes (0-4) | SensorEntity | Load management mode |
| `wallbox_cp_availability_text` | Wallbox CP Availability Text | `sensor.cp_availability` | Binary status | SensorEntity | Available/Not available |
| `wallbox_plug_lock_status_text` | Wallbox Plug Lock Status Text | `sensor.plug_lock_status` | Binary status | SensorEntity | Locked/Unlocked |

### 2.6 Error Code Decoding Template
Bitfield analysis of error codes (Error Codes 1)

| Template Unique ID | Name | Input Sensor | Decoding | Entity Type | Notes |
|---|---|---|---|---|---|
| `wallbox_error_codes_text` | Wallbox Error Codes Text | `sensor.error_codes_1` | 16-bit flags → error list | SensorEntity | Decodes: RCM, vehicle state E, diode check, MCB, RCD, contact weld, backend, actuator lock, actuator stuck, firmware update, tilt, cable, overload, no power |

### 2.7 Hardware Information Template
Concatenate multi-word string registers

| Template Unique ID | Name | Input Sensors | Result | Entity Type |
|---|---|---|---|---|
| `wallbox_chargepoint_model` | Wallbox Chargepoint Model | `sensor.chargepoint_model_1-5` | Full model string | SensorEntity |

### 2.8 Cost Calculation Templates
Compute CHF costs from kWh and price

| Template Unique ID | Name | Unit | State Class | Inputs | Formula | Entity Type |
|---|---|---|---|---|---|---|
| `wallbox_kosten_gesamt_chf` | Wallbox Kosten Gesamt CHF | CHF | total | `sensor.wallbox_sessions.total_kwh`, `input_number.wallbox_price_per_kwh` | kWh × price | SensorEntity |
| `wallbox_kosten_aktueller_monat_chf` | Wallbox Kosten Aktueller Monat CHF | CHF | total | Monthly summary, price | Current month kWh × price | SensorEntity |

### 2.9 Vehicle-Specific Totals
Extract from REST API session data

| Template Unique ID | Name | Unit | State Class | Purpose | Entity Type |
|---|---|---|---|---|---|
| `wallbox_kwh_kessi_gesamt` | Wallbox kWh Kessi Gesamt | kWh | total | Vehicle 1 lifetime energy | SensorEntity |
| `wallbox_kwh_tessi_gesamt` | Wallbox kWh Tessi Gesamt | kWh | total | Vehicle 2 lifetime energy | SensorEntity |

### 2.10 Monthly Summary Template

| Template Unique ID | Name | Unit | State Class | Purpose | Entity Type |
|---|---|---|---|---|---|
| `wallbox_kwh_aktueller_monat` | Wallbox kWh Aktueller Monat | kWh | total | Current month energy | SensorEntity |

**Total Template Sensors**: 16 SensorEntity instances

---

## 3. INPUT HELPERS (User-Configurable Settings)

### 3.1 Input Boolean Helpers (SwitchEntity/BooleanEntity)

| Unique ID | Type | Name (DE) | Icon | Purpose | Default | Entity Type |
|---|---|---|---|---|---|---|
| `wallbox_cp_availability` | boolean | Wallbox CP Verfügbarkeit | `mdi:ev-station` | Enable/disable CP | false | SwitchEntity or BooleanEntity |
| `wallbox_pause_charging` | boolean | Wallbox Laden pausieren | `mdi:pause` | Pause charging session | false | SwitchEntity or BooleanEntity |

### 3.2 Input Number Helpers (NumberEntity)

| Unique ID | Type | Name (DE) | Unit | Min | Max | Step | Mode | Icon | Purpose | Entity Type |
|---|---|---|---|---|---|---|---|---|---|---|
| `wallbox_hems_current_limit` | number | Wallbox HEMS Stromlimit | A | 0 | 16 | 1 | slider | `mdi:lightning-bolt` | Dynamic current limit | NumberEntity |
| `wallbox_safe_current` | number | Wallbox Safe Current | A | 0 | 32 | 1 | slider | `mdi:shield` | Safety current threshold | NumberEntity |
| `wallbox_comm_timeout` | number | Wallbox Kommunikations-Timeout | s | 1 | 300 | 1 | slider | `mdi:timer` | Modbus timeout | NumberEntity |

### 3.3 Input Select Helpers (SelectEntity)

| Unique ID | Type | Name (DE) | Icon | Options | Purpose | Entity Type |
|---|---|---|---|---|---|---|
| `wallbox_month_filter` | select | Wallbox Monatsfilter | `mdi:calendar-filter` | ["Alle", ...] | Filter sessions by month | SelectEntity |
| `wallbox_rfid_selector` | select | Wallbox RFID auswählen | `mdi:card-account-details` | ["Bitte auswählen...", ...] | Select RFID to assign vehicle | SelectEntity |

### 3.4 Input Text Helpers (TextEntity)

| Unique ID | Type | Name (DE) | Max Length | Icon | Purpose | Entity Type |
|---|---|---|---|---|---|---|
| `wallbox_vehicle_1_rfid` | text | Fahrzeug 1 RFID | 20 | `mdi:card-account-details` | RFID for vehicle 1 | TextEntity |
| `wallbox_vehicle_1_name` | text | Fahrzeug 1 Name | 30 | `mdi:car-electric` | Name for vehicle 1 | TextEntity |
| `wallbox_vehicle_2_rfid` | text | Fahrzeug 2 RFID | 20 | `mdi:card-account-details` | RFID for vehicle 2 | TextEntity |
| `wallbox_vehicle_2_name` | text | Fahrzeug 2 Name | 30 | `mdi:car-electric` | Name for vehicle 2 | TextEntity |
| `wallbox_vehicle_3_rfid` | text | Fahrzeug 3 RFID | 20 | `mdi:card-account-details` | RFID for vehicle 3 | TextEntity |
| `wallbox_vehicle_3_name` | text | Fahrzeug 3 Name | 30 | `mdi:car-electric` | Name for vehicle 3 | TextEntity |
| `wallbox_vehicle_4_rfid` | text | Fahrzeug 4 RFID | 20 | `mdi:card-account-details` | RFID for vehicle 4 | TextEntity |
| `wallbox_vehicle_4_name` | text | Fahrzeug 4 Name | 30 | `mdi:car-electric` | Name for vehicle 4 | TextEntity |
| `wallbox_vehicle_name_new` | text | Neuer Fahrzeugname | 30 | `mdi:car-electric` | New vehicle name input | TextEntity |

**Total Input Helpers**: 2 SwitchEntity + 3 NumberEntity + 2 SelectEntity + 9 TextEntity = 16 entities

---

## 4. REST API ENDPOINTS & DATA FETCHING

### 4.1 API Configuration

| Property | Value |
|---|---|
| **Base URL** | `http://<WALLBOX_IP>/api/v1` |
| **Authentication** | Bearer Token (OCPP-style auth) |
| **Login Endpoint** | `/AuthManagement/login` |
| **Nonce Requirement** | Yes, `X-Nonce` header required |
| **Default Timeout** | 10-30 seconds |

### 4.2 Charging Transaction History Endpoint

**Endpoint**: `/ChargingTransactionHistory/ReadFromTo`

**Method**: GET

**Parameters**:
```
skip: 0 (offset)
take: 50-200 (limit)
from: 2024-01-01T00:00:00.000Z (start date ISO)
to: now (end date ISO)
```

**Response Structure**:
```json
{
  "list": [
    {
      "ocppTransactionId": "unique_id",
      "startTimestamp": "2024-07-20T10:30:00Z",
      "stopTimestamp": "2024-07-20T11:45:30Z",
      "chargedEnergy": 12.5 (kWh),
      "chargedTime": "1:15:30",
      "formattedChargedTime": "01:15:30",
      "userToken": { "identifier": "RFID_CODE" },
      "whitelistEntryFirstName": "Vehicle Name",
      "startMeterValue": 1000.5 (kWh),
      "stopMeterValue": 1012.99 (kWh),
      "stopReason": "Remote|Local|EVDisconnected|Emergency",
      "startTransactionStatus": "Successful",
      "stopTransactionStatus": "Successful",
      "isAborted": false,
      "authorizationOption": "RFID|PIN|Manual"
    }
  ]
}
```

**Update Frequency**: 1 hour (via automation/script)

**Used By**:
- `fetch_charging_sessions.py` → Stores to `/config/wallbox_sessions.json`
- `fetch_system_logs.py` → Derives system events

### 4.3 System Events Endpoint (Optional)

**Endpoint**: `/SystemManagement/SystemEvents`

**Method**: GET

**Response Structure**:
```json
{
  "systemEvents": [
    {
      "timestamp": "2024-07-20T10:30:00Z",
      "eventId": "EVENT_ID",
      "level": "INFO|WARNING|ERROR",
      "description": "Event description"
    }
  ]
}
```

**Status**: May return 404 on some firmware versions (1.5.41 confirmed)

**Used By**: `fetch_system_events.py` → Stores to `/config/wallbox_system_events.json`

### 4.4 Data Files Generated

| File | Location | Source Script | Content | Update Freq |
|---|---|---|---|---|
| `wallbox_sessions.json` | `/config/` | `fetch_charging_sessions.py` | Charging history, monthly summary, vehicle totals, costs | 1 hour |
| `wallbox_system_logs.json` | `/config/` | `fetch_system_logs.py` | Derived transaction logs | 1 hour |
| `wallbox_system_events.json` | `/config/` | `fetch_system_events.py` | System events | 1 hour |
| `wallbox_vehicles.json` | `/config/` | `assign_vehicle.py`, `write_vehicles.py` | RFID → Vehicle name mapping | On change |
| `wallbox_config.json` | `/config/` | Manual | Price per kWh configuration | On change |

---

## 5. PYTHON SCRIPTS (Action Triggers & Data Processors)

### 5.1 `fetch_charging_sessions.py`

**Purpose**: Fetch charging transaction history via REST API, compute costs, aggregate by month/vehicle

**Triggers**: Scheduled (1-hour automation) or manual

**Inputs**:
- Environment: `WALLBOX_PASS` (installer password), `WALLBOX_URL` (API base URL)
- Files: `/config/wallbox_vehicles.json` (RFID mapping), `/config/wallbox_config.json` (price/kWh)

**Process**:
1. Get nonce from `/Nonce` endpoint
2. Login with installer credentials → obtain Bearer token
3. Query `/ChargingTransactionHistory/ReadFromTo` with date range
4. Filter out incomplete sessions (stop timestamp = "0001-01-01")
5. Map RFID to vehicle names from `wallbox_vehicles.json`
6. Calculate energy (kWh) and cost (CHF) per session
7. Aggregate by month and vehicle
8. Sort descending by start time
9. Output JSON to `/config/wallbox_sessions.json`

**Output**: REST-sourced sensor with attributes
- **State**: Always "OK" (or error state)
- **Attributes**:
  - `count`: Total sessions
  - `total_kwh`: Lifetime energy
  - `total_cost_chf`: Lifetime cost
  - `price_per_kwh_chf`: Current electricity price
  - `last_session_kwh`: Energy from last completed session
  - `last_session_start`: Timestamp
  - `last_vehicle`: Vehicle name
  - `vehicles`: List of unique vehicles
  - `vehicle_totals`: Dict of kWh per vehicle
  - `monthly_summary`: Array of monthly aggregates with `by_vehicle` breakdown
  - `sessions`: Array of last 50 sessions

**Migration Mapping**: 
- **Entity Type**: `RestSensorEntity` or `SensorEntity` (REST integration)
- **Unique ID**: `wallbox_sessions`
- **State**: File/REST state
- **Attributes**: Monthly/vehicle data

### 5.2 `fetch_system_logs.py`

**Purpose**: Derive system log entries from transaction data (since `/SystemManagement/SystemEvents` may not exist)

**Triggers**: Scheduled (1-hour automation) or manual

**Inputs**:
- Environment: `WALLBOX_PASS`, `WALLBOX_URL`
- Files: `/config/wallbox_vehicles.json`

**Process**:
1. Authentication same as session script
2. Query transaction history
3. For each transaction, create START and STOP log entries
4. Decode transaction status, stop reason, abort flag
5. Assign log level: ERROR if failed, WARNING if abnormal stop, INFO otherwise
6. Output JSON to `/config/wallbox_system_logs.json`

**Log Structure**:
```json
[
  {
    "timestamp": "ISO datetime",
    "event_id": "TX-{ocpp_id}-START|STOP",
    "level": "INFO|WARNING|ERROR",
    "description": "Human-readable event",
    "vehicle": "Vehicle name",
    "rfid": "RFID code"
  }
]
```

**Migration Mapping**:
- **Entity Type**: `SensorEntity` (read-only, file-based)
- **Unique ID**: `wallbox_system_logs`
- **Attributes**: Derived from transactions

### 5.3 `fetch_system_events.py`

**Purpose**: Fetch system events from `/SystemManagement/SystemEvents` endpoint

**Triggers**: Scheduled (1-hour automation) or manual

**Inputs**:
- Environment: `WALLBOX_PASS`, `WALLBOX_URL`

**Process**:
1. Authentication same as above
2. Query `/SystemManagement/SystemEvents`
3. Handle 404 gracefully (endpoint optional)
4. Standardize response format
5. Sort by timestamp descending
6. Output JSON to `/config/wallbox_system_events.json`

**Event Structure**:
```json
[
  {
    "timestamp": "ISO datetime",
    "event_id": "EVENT_ID",
    "level": "INFO|WARNING|ERROR",
    "description": "Event text",
    "details": { /* raw event object */ }
  }
]
```

**Migration Mapping**:
- **Entity Type**: `SensorEntity` (read-only, REST-based)
- **Unique ID**: `wallbox_system_events`
- **Attributes**: Events list

### 5.4 `assign_vehicle.py`

**Purpose**: Assign a single vehicle name to an RFID and persist mapping

**Triggers**: Automation (on button press in dashboard)

**Inputs**:
- Environment: `RFID_OPTION` (format: "RFID — Vehicle Name"), `VEHICLE_NAME`

**Process**:
1. Parse RFID from option string (handle delimiters)
2. Load existing `/config/wallbox_vehicles.json`
3. Add/update RFID → name mapping
4. Save JSON

**Migration Mapping**:
- **Entity Type**: `ButtonEntity` (triggers service call)
- **Service**: Custom service `mennekes_amtron.assign_vehicle`
- **Parameters**: `rfid`, `name`

### 5.5 `write_vehicles.py`

**Purpose**: Bulk write 4 vehicle RFID-to-name mappings

**Triggers**: Automation (on button press for "save all 4 slots")

**Inputs**:
- Environment: `RFID1..RFID4`, `NAME1..NAME4` (paired sets)

**Process**:
1. Read environment variables
2. Build mapping for 4 vehicles
3. Overwrite `/config/wallbox_vehicles.json`
4. Print confirmation

**Migration Mapping**:
- **Entity Type**: `ButtonEntity` (triggers bulk update)
- **Service**: Custom service `mennekes_amtron.write_vehicles`
- **Parameters**: `rfid1..4`, `name1..4`

### 5.6 `generate_dashboard.py`

**Purpose**: Generate Lovelace dashboard YAML with properly escaped Jinja2 templates

**Triggers**: Manual (development)

**Output**: Dashboard JSON for `/api/lovelace/dashboards`

**Migration Mapping**:
- **Not needed in integration**: Dashboard provisioning handled by integration configuration
- **Alternative**: Use `hass.helpers.config_validation` to provide dashboard template

---

## 6. DASHBOARD STRUCTURE

### 6.1 Main Dashboard Layout

**Config**:
- Title: "Mennekes AMTRON Wallbox"
- Path: `/lovelace/wallbox`
- Icon: `mdi:ev-station`
- Views: 3 (Übersicht, History, Konfiguration)

### 6.2 View 1: Übersicht (Overview)

**Path**: `wallbox-main`

**Cards**:

1. **Status Card** (Entities)
   - Chargepoint Model
   - Software Version
   - Charging Status (template)
   - Vehicle State (template)
   - CP Availability (template)
   - Plug Lock Status (template)
   - Error Codes (template)
   - Protocol Version

2. **Current Session Card** (Entities)
   - Session Energy (kWh template)
   - Charge Duration (formatted template)
   - Signaled Current (Modbus)
   - Max Current EV (Modbus)

3. **Energy Card** (Entities, kWh converted)
   - Total Energy
   - L1, L2, L3 Energy

4. **Power Card** (Entities)
   - Total Power
   - L1, L2, L3 Power

5. **Voltage & Current Card** (Entities)
   - L1, L2, L3 Voltage
   - L1, L2, L3 Current (Ampere converted)

6. **Limits Card** (Entities, read-only display)
   - HEMS Current Limit
   - Operator Current Limit
   - Safe Current
   - Comm Timeout

7. **DLM Card** (Entities)
   - DLM Mode (text template)
   - Connected Slaves
   - Available/Applied current per phase

### 6.3 View 2: History

**Path**: `wallbox-history` (Panel type)

**Cards**:

1. **Statistics & Filter** (Entities)
   - Session count sensor (REST)
   - Total energy (template)
   - Total costs CHF (template)
   - Vehicle-specific totals (templates)
   - Monthly total (template)
   - Current month cost (template)
   - Month filter select

2. **Monthly Consumption Chart** (apexcharts-card)
   - Data source: `sensor.wallbox_sessions` attributes
   - Type: Stacked column chart
   - Variables: Kessi (vehicle 1), Tessi (vehicle 2)
   - Timespan: 6 months
   - Metrics: kWh per vehicle per month

3. **Monthly Table** (Markdown)
   - Dynamic table from monthly_summary
   - Columns: Month | Vehicle1 kWh | CHF | Vehicle2 kWh | CHF | Total kWh | Total CHF
   - Filter by month

4. **Charging Sessions Table** (Markdown)
   - Dynamic table from sessions array
   - Columns: Date | Vehicle | Duration | Energy (kWh) | Cost (CHF)
   - Filterable by month
   - Shows vehicle totals below table

### 6.4 View 3: Konfiguration

**Path**: `wallbox-config`

**Cards**:

1. **Vehicle Assignment** (Entities)
   - RFID selector (select helper)
   - New vehicle name (text helper)

2. **Assign Button** (Button)
   - Service: `script.wallbox_zuweise_fahrzeug`
   - Action: Calls `assign_vehicle.py` + reload script

3. **Known Vehicles** (Markdown)
   - Dynamic list of RFIDs seen in sessions
   - Instructions for assignment

4. **Wallbox Settings** (Entities)
   - Price per kWh (number helper)
   - HEMS limit (number helper for writing)
   - Safe current (number helper for writing)
   - Comm timeout (number helper for writing)
   - CP Availability (boolean helper)
   - Pause Charging (boolean helper)

5. **Manual RFID Management** (Entities)
   - 4 slots × 2 fields (RFID + Name)
   - Text helpers

6. **Save All Slots Button** (Button)
   - Service: `script.wallbox_aktualisiere_fahrzeuge`
   - Action: Calls `write_vehicles.py` + reload script

**Dashboard Mandatory Items** (must migrate):
- Overview tab with status/meter display
- History tab with session data
- Configuration tab for vehicle assignment

**Dashboard Optional Items** (nice-to-have):
- apexcharts-card for charts (requires custom card)
- Markdown template rendering (core feature)

---

## 7. ENTITY TYPE MAPPING SUMMARY

### Entity Type Distribution

| Home Assistant Entity Type | Count | Source | Notes |
|---|---|---|---|
| **SensorEntity** | 68 | Modbus registers (read-only) | Modbus TCP input_type: holding |
| **SensorEntity** | 16 | Template sensors | Jinja2 templates from templates/wallbox.yaml |
| **SensorEntity** | 3 | REST API data | wallbox_sessions, system_logs, system_events |
| **NumberEntity** | 4 | Input + Modbus | 3 input_number + 1 writable Modbus register |
| **SwitchEntity** | 2 | Input boolean | CP availability, pause charging |
| **SelectEntity** | 2 | Input select | Month filter, RFID selector |
| **TextEntity** | 9 | Input text | 8 RFID/vehicle pairs + 1 new vehicle name |
| **ButtonEntity** | 2 | Script triggers | Assign single vehicle, write 4 vehicles |
| **DiagnosticEntity** | ? | Error/system info | Firmware, protocol version (optional) |
| **Total Entities** | **106+** | | In fully migrated integration |

### Configuration Flow

```
Config Entry (config_entries.py)
├── Wallbox IP address
├── Wallbox password (sensitive)
├── Price per kWh (CHF)
├── Update frequency (seconds)
└── Enable features (Modbus, REST API, templates)

        ↓
        
ModbusCoordinator (via pymodbus)
├── Reads 68 registers every X seconds
├── Updates SensorEntity instances
└── Makes data available to templates

        ↓

TemplateEntity instances (16)
├── Read coordinator data
├── Apply transformations
├── Update state/attributes

        ↓

RestApiCoordinator (fetch_charging_sessions.py)
├── Runs scheduled (1 hour)
├── Updates REST sensor attributes
└── Used by cost/vehicle templates

        ↓

Services (available for automation)
├── mennekes_amtron.assign_vehicle
└── mennekes_amtron.write_vehicles
```

---

## 8. MIGRATION CHECKLIST

### Phase 1: Core Modbus Integration

- [ ] Create `mennekes_amtron/config_entries.py` with configuration UI
- [ ] Create `mennekes_amtron/coordinator.py` with ModbusCoordinator
- [ ] Create `mennekes_amtron/entities.py` base class for all entities
- [ ] Implement `mennekes_amtron/sensor.py` for all 68 + 3 REST sensors
- [ ] Implement `mennekes_amtron/number.py` for 4 number entities (including writable Modbus)
- [ ] Implement `mennekes_amtron/switch.py` for 2 boolean inputs
- [ ] Implement `mennekes_amtron/select.py` for 2 select inputs
- [ ] Implement `mennekes_amtron/text.py` for 9 text inputs
- [ ] Implement `mennekes_amtron/button.py` for 2 script trigger buttons
- [ ] Create manifest.json with dependencies (pymodbus)

### Phase 2: Template Sensors & REST Integration

- [ ] Implement template sensor coordinator for 16 template sensors
- [ ] Implement REST API coordinator for `fetch_charging_sessions.py`
- [ ] Integrate `fetch_system_logs.py` and `fetch_system_events.py`
- [ ] Add device registry entries for Mennekes AMTRON device

### Phase 3: Services & Automation

- [ ] Implement `assign_vehicle` service
- [ ] Implement `write_vehicles` service
- [ ] Add script helpers for automation triggers
- [ ] Test service calls from dashboard buttons

### Phase 4: Dashboard Provisioning

- [ ] Provision Lovelace dashboard (if desired via integration)
- [ ] Or provide dashboard template file in integration package

### Phase 5: Testing & Validation

- [ ] Unit tests for coordinator
- [ ] Integration tests for entity updates
- [ ] Test error handling (connection loss, invalid data)
- [ ] Validate all 106+ entities are created
- [ ] Test dashboard display and interactivity

---

## 9. KEY IMPLEMENTATION NOTES

### 9.1 Data Type Handling

**Modbus Specifics**:
- `uint16`: Single register (2 bytes)
- `uint32`: Two consecutive registers (4 bytes) – must handle byte order
- `string`: Multiple consecutive registers (count × 2 bytes) – requires decoding

**Critical**: The recent commit `08ad342` mentions "Correct int32 register byte order for accurate meter values" – verify byte order handling in integration.

### 9.2 Unit Conversions

- **Current**: mA → A (divide by 1000) – done in templates
- **Energy**: Wh → kWh (divide by 1000) – done in templates
- **Time**: seconds → HH:MM:SS (format string) – done in templates

### 9.3 State Class Notes

- `total_increasing`: Energy/cumulative meters (never reset)
- `measurement`: Instantaneous values (power, current, voltage)
- `total`: Calculated totals (costs)

### 9.4 Device Class Matching

- `energy`: Energy in Wh/kWh
- `power`: Power in W
- `current`: Current in A/mA
- `voltage`: Voltage in V
- `enum`: Status fields with discrete values

### 9.5 RFID Vehicle Mapping

Currently stored in `/config/wallbox_vehicles.json` (external file). In integration:
- Option 1: Store in Home Assistant storage (`hass.data` or data file)
- Option 2: Persist to external file (same as current)
- Option 3: Use entity attributes (vehicle names stored as select/text entity states)

### 9.6 REST API & Authentication

- **Nonce-based OCPP auth**: Requires 2-step auth (get nonce, then login)
- **Bearer token expiry**: Not documented – assume long-lived or refresh per call
- **Endpoint availability**: `/SystemManagement/SystemEvents` may return 404 – handle gracefully
- **Data staleness**: 1-hour fetch schedule – acceptable for historical data

### 9.7 Dashboard Components

**Must Work**:
- Markdown tables with Jinja2 templates
- Entities cards with icon/name display
- Button cards calling services

**Requires Custom Card**:
- `apexcharts-card` for monthly consumption chart (not core)
- Alternative: Use `history-stats` or `mini-graph-card` if apexcharts unavailable

---

## 10. VALIDATION CHECKLIST FOR MIGRATION

After implementation, verify:

1. **Modbus Connectivity**
   - [ ] All 68 registers readable
   - [ ] Byte order correct for uint32 values
   - [ ] Timeout/retry logic working
   - [ ] Error recovery functional

2. **Template Sensors**
   - [ ] All 16 templates update when source data changes
   - [ ] Unit conversions accurate
   - [ ] Status mappings human-readable
   - [ ] Cost calculations correct

3. **REST Integration**
   - [ ] Authentication working
   - [ ] Session data fetched hourly
   - [ ] Monthly aggregation correct
   - [ ] Vehicle mapping persisted

4. **Dashboard**
   - [ ] All tabs display without errors
   - [ ] Charts render (if using apexcharts)
   - [ ] Markdown tables show data
   - [ ] Buttons trigger services

5. **Services**
   - [ ] Vehicle assignment persists
   - [ ] Bulk write updates all 4 slots
   - [ ] Dashboard updates after service calls

6. **Configuration**
   - [ ] Config entry UI accepts all required fields
   - [ ] Credentials stored securely
   - [ ] Update frequency configurable
   - [ ] Options flow available for runtime changes

---

## Summary Statistics

| Category | Count |
|---|---|
| **Modbus Registers** | 68 read-only + 1 writable = 69 |
| **Template Sensors** | 16 |
| **REST API Sensors** | 3 |
| **Input Helpers** | 16 (2 switch + 3 number + 2 select + 9 text) |
| **Services** | 2 |
| **Dashboard Views** | 3 |
| **Total Entities** | 106+ |
| **Entity Types** | 9 (Sensor, Number, Switch, Select, Text, Button, Diagnostic, etc.) |

**Architecture**: Distributed Coordinator pattern
- ModbusCoordinator: Real-time Modbus TCP polling
- RestApiCoordinator: Scheduled hourly REST API calls
- TemplateCoordinator: Reactive template updates

**Language**: German (all entity names, descriptions)

**Dependencies**: pymodbus, aiohttp (optional for REST)

