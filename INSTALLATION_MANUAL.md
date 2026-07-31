# Mennekes AMTRON Wallbox – Manual Installation

[Deutsch (Schnellstart)](README.md) · [Manuelle Installation (Deutsch)](INSTALLATION_MANUELL.md) · [English (quick start)](README.en.md) · **Manual installation (English)**

> This page describes the **full manual setup** with template sensors, helpers, Python scripts
> and the full version of the dashboard. For the automated path via HACS and the configuration
> dialog, the [quick start](README.en.md) is enough.

Complete integration of a Mennekes AMTRON wallbox into Home Assistant. Supports the entire
**AMTRON 4You 400/500** and **AMTRON 4Business 600/700** portfolio — all of these series use the
same Modbus TCP register set (see [Supported models](#supported-models)):
- **Real-time monitoring** via Modbus TCP (voltage, current, power, charging status)
- **Charging sessions** via REST API (session history, vehicle assignment, costs)
- **Control** of HEMS limit, safe current, availability, charging pause
- **Dashboard** with ApexCharts bar chart, monthly table, session list

---

## 📦 Installation

Installing the integration itself and the configuration dialog are covered in the
**[quick start](README.en.md)** — including the HACS button and a screenshot of the dialog.

This page picks up where the quick start ends: cloning the repository and setting up the YAML parts
(template sensors, helpers, scripts, automations).

```bash
git clone https://github.com/nobelp/mennekes-amtron-ha.git ~/HA_Menneckes
```

---

## ✅ Home Assistant Quality Scale

| Aspect | Status | Details |
|--------|--------|---------|
| **Code Quality** | ⭐⭐⭐⭐ | Python scripts with error handling |
| **Documentation** | ⭐⭐⭐⭐⭐ | Comprehensive in German + English |
| **Testing** | ⭐⭐⭐ | Tested on HA 2026.5.4 + AMTRON 730 |
| **Maintainability** | ⭐⭐⭐⭐ | Modular YAML + Python structure |
| **Security** | ⭐⭐⭐⭐ | No hardcoded passwords/IPs, .env support |

---

## Overview: How Everything Connects

```
┌─────────────────────┐     Modbus TCP :502      ┌────────────────────┐
│  Home Assistant     │ ◄──────────────────────► │  Mennekes Wallbox  │
│  192.x.x.x          │                           │  192.x.x.x         │
│                     │     REST API :80          │                    │
│  (Docker on NAS)    │ ◄──────────────────────► │  (WiFi + GSM)      │
└─────────────────────┘                           └────────────────────┘
        │
        │ reads/writes
        ▼
  /config/wallbox_sessions.json    (charging sessions + monthly data)
  /config/wallbox_vehicles.json    (RFID → vehicle name mapping)
  /config/wallbox_config.json      (electricity price CHF/kWh)
  /config/wallbox_fetch.log        (fetch log for debugging)
```

### Data Paths & Frequency

| Source | Frequency | Target |
|--------|-----------|--------|
| Modbus TCP registers | every 30s | HA sensors (voltage, current, power…) |
| REST API `/ChargingTransactionHistory` | hourly + HA start | `/config/wallbox_sessions.json` |
| `wallbox_sessions.json` | hourly (cat) | `sensor.wallbox_sessions` |
| `sensor.wallbox_sessions` attributes | live (template) | cost sensors, dashboard |
| Dashboard (ApexCharts) | on page load | bar chart from `monthly_summary` |

---

## Supported models

The **AMTRON 4You 400 and 500** and **AMTRON 4Business 600 and 700** series communicate
identically — same Modbus TCP server on port 502, unit ID 1, holding registers only, identical
register set. The integration therefore covers this entire portfolio, including sub-variants such
as the 4Business 730 or the 4You 550.

| Series | Support |
|---|---|
| AMTRON 4You 400 | ✅ identical register set |
| AMTRON 4You 500 | ✅ identical register set |
| AMTRON 4Business 600 | ✅ identical register set |
| AMTRON 4Business 700 | ✅ identical register set (tested on 730 11 C2) |
| Other Mennekes series | ❌ different or no Modbus register set |

You do not need to configure the model: the integration reads article name, firmware version and
serial number from the wallbox via `GET /api/v1/PublicInfo` at startup and passes them into the
Home Assistant device info.

**Device requirements:**

- Modbus interface **protocol version 1.5** (firmware 1.5.x). Registers below 600 also exist in
  protocol version 1.0; the HEMS and phase-switch registers 2000–2030 require 1.5.
- Modbus TCP must be enabled. Register **2010** reports the state: `0` = server inactive,
  `1` = read only, `2` = read and write. The write features (HEMS limit, safe current) require `2`.

---

## Hardware Configuration

Example values from the reference installation — replace them with your own:

- **Wallbox**: Mennekes AMTRON 4Business 730 11 C2
- **Firmware**: 1.5.41
- **Primary IP**: `192.x.x.x` (WiFi) — replace with your wallbox IP
- **Fallback IP**: `10.x.x.x` (GSM/mobile) — optional, only if available
- **Modbus**: Port 502, Slave ID 1
- **REST API**: Port 80 (HTTP)
- **HA Host**: `192.x.x.x:8123` (Docker on Synology NAS) — replace with your HA IP
- **HA Config**: `/config/` in the Home Assistant container

---

## Environment Variables & Configuration

### Creating the .env File

The Python scripts require environment variables for the wallbox connection. Copy `.env.example` and adjust the values:

```bash
cp .env.example .env
```

Contents of `.env` (edit with your values):

```bash
# Mennekes Wallbox Configuration
WALLBOX_URL=http://192.x.x.x/api/v1    # Wallbox REST API URL (replace 192.x.x.x)
WALLBOX_PASS=SAMPLE_PASSWORD            # Installer password (replace with your password)

# Home Assistant (optional)
HA_HOST=192.x.x.x                       # Home Assistant host IP (replace with your HA IP)
HA_TOKEN=SAMPLE_API_TOKEN               # Long-lived access token (optional)
```

### Running Scripts with Environment Variables

```bash
# Using .env file
source .env
python3 python_scripts/fetch_charging_sessions.py

# Or pass directly
WALLBOX_PASS=your-password python3 python_scripts/fetch_charging_sessions.py

# Or as argument
python3 python_scripts/fetch_charging_sessions.py your-password
```

> **Important**: `.env` is ignored by Git and should **not** be checked into version control. Use `.env.example` for documentation purposes.

---

## Full Fresh Installation (Step by Step)

### 1. Copy Files from Workspace to HA

```bash
# Modbus configuration
cp modbus_wallbox.yaml /config/

# Helper entities
cp input_number_wallbox.yaml /config/
cp input_boolean_wallbox.yaml /config/
cp input_select_wallbox.yaml /config/
cp input_text_wallbox.yaml /config/

# Template sensors
cp templates/wallbox.yaml /config/templates/

# Python scripts
cp python_scripts/fetch_charging_sessions.py /config/python_scripts/
cp python_scripts/run_wallbox_fetch.sh /config/python_scripts/
cp python_scripts/write_vehicles.py /config/python_scripts/
cp python_scripts/assign_vehicle.py /config/python_scripts/

# Configuration files
cp wallbox_config.json /config/
cp wallbox_vehicles.json /config/

# Dashboard: set up in step 6 — the storage file only takes effect once the
# dashboard is registered with the URL dashboard-wallbox.
```

### 2. Update `configuration.yaml`

Add the following blocks to the existing `configuration.yaml`:

```yaml
# Recorder: exclude session sensor (large JSON attributes would
# freeze the frontend when ApexCharts fetches data)
recorder:
  exclude:
    entities:
      - sensor.wallbox_sessions

# Wallbox Modbus + Helpers
modbus: !include modbus_wallbox.yaml
input_number: !include input_number_wallbox.yaml
input_boolean: !include input_boolean_wallbox.yaml
input_select: !include input_select_wallbox.yaml
input_text: !include input_text_wallbox.yaml

# command_line sensors (HA 2022.11+ format – IMPORTANT: top-level, not under "sensor:")
command_line:
  - sensor:
      name: "Wallbox Software Version"
      unique_id: wallbox_software_version
      command: "curl -sf http://192.x.x.x/api/v1/PublicInfo | python3 -c \"import json,sys; d=json.load(sys.stdin); print(d['currentVersion'])\"" # Replace 192.x.x.x
      scan_interval: 3600

  - sensor:
      name: "Wallbox Sessions"
      unique_id: wallbox_sessions
      command: "cat /config/wallbox_sessions.json 2>/dev/null || echo '{\"count\":0,\"sessions\":[],\"total_kwh\":0,\"monthly_summary\":[],\"vehicles\":[],\"vehicle_totals\":{}}'"
      value_template: "{{ value_json.count | int(0) }}"
      json_attributes:
        - sessions
        - total_kwh
        - monthly_summary
        - vehicles
        - vehicle_totals
        - last_session_kwh
        - last_vehicle
      scan_interval: 3600

# Shell commands
shell_command:
  wallbox_fetch_sessions: "/bin/sh /config/python_scripts/run_wallbox_fetch.sh"

  wallbox_write_vehicles: >-
    RFID1="{{ states('input_text.wallbox_vehicle_1_rfid') }}"
    NAME1="{{ states('input_text.wallbox_vehicle_1_name') }}"
    RFID2="{{ states('input_text.wallbox_vehicle_2_rfid') }}"
    NAME2="{{ states('input_text.wallbox_vehicle_2_name') }}"
    RFID3="{{ states('input_text.wallbox_vehicle_3_rfid') }}"
    NAME3="{{ states('input_text.wallbox_vehicle_3_name') }}"
    RFID4="{{ states('input_text.wallbox_vehicle_4_rfid') }}"
    NAME4="{{ states('input_text.wallbox_vehicle_4_name') }}"
    python3 /config/python_scripts/write_vehicles.py

  wallbox_assign_vehicle: >-
    RFID_OPTION="{{ states('input_select.wallbox_rfid_selector') }}"
    VEHICLE_NAME="{{ states('input_text.wallbox_vehicle_name_new') }}"
    python3 /config/python_scripts/assign_vehicle.py
```

> **Important**: `recorder: exclude` prevents the sensor with its large JSON attributes from being written to the recorder database every hour. Without this setting, the frontend freezes when opening the History page (ApexCharts tries to load the complete entity history).

### 3. `automations.yaml` – Add Automation

```yaml
- id: '1780407000000'
  alias: Wallbox Update Charging Sessions
  description: Fetches sessions from the API (on startup and hourly), updates sensor and both dropdowns
  triggers:
  - event: start
    trigger: homeassistant
  - trigger: time_pattern
    hours: /1
  conditions: []
  actions:
  - action: shell_command.wallbox_fetch_sessions
    data: {}
  - action: homeassistant.update_entity
    target:
      entity_id: sensor.wallbox_sessions
  - delay: "00:00:04"
  - action: input_select.set_options
    target:
      entity_id: input_select.wallbox_month_filter
    data:
      options: >
        {{ ['All'] + ((state_attr('sensor.wallbox_sessions', 'monthly_summary') or []) | map(attribute='month_label') | list) }}
  - action: input_select.set_options
    target:
      entity_id: input_select.wallbox_rfid_selector
    data:
      options: >
        {% set sessions = state_attr('sensor.wallbox_sessions', 'sessions') %}
        {% set ns = namespace(seen=[], opts=[]) %}
        {% if sessions %}{% for s in sessions %}{% if s.rfid and s.rfid not in ns.seen %}{% set ns.seen = ns.seen + [s.rfid] %}{% set ns.opts = ns.opts + [s.rfid ~ ' — ' ~ s.vehicle] %}{% endif %}{% endfor %}{% endif %}
        {{ ['Please select...'] + ns.opts }}
  mode: single
```

### 4. `scripts.yaml` – Add Scripts

```yaml
# Script 1: Assign RFID to a vehicle name (via dropdown)
wallbox_assign_vehicle:
  alias: "Assign Vehicle RFID"
  icon: mdi:card-account-details-outline
  mode: single
  sequence:
    - action: shell_command.wallbox_assign_vehicle
    - action: shell_command.wallbox_fetch_sessions
    - delay: "00:00:20"
    - action: homeassistant.update_entity
      target:
        entity_id: sensor.wallbox_sessions
    - delay: "00:00:04"
    - action: input_select.set_options
      target:
        entity_id: input_select.wallbox_month_filter
      data:
        options: >
          {{ ['All'] + ((state_attr('sensor.wallbox_sessions', 'monthly_summary') or []) | map(attribute='month_label') | list) }}
    - action: input_select.set_options
      target:
        entity_id: input_select.wallbox_rfid_selector
      data:
        options: >
          {% set sessions = state_attr('sensor.wallbox_sessions', 'sessions') %}
          {% set ns = namespace(seen=[], opts=[]) %}
          {% if sessions %}{% for s in sessions %}{% if s.rfid and s.rfid not in ns.seen %}{% set ns.seen = ns.seen + [s.rfid] %}{% set ns.opts = ns.opts + [s.rfid ~ ' — ' ~ s.vehicle] %}{% endif %}{% endfor %}{% endif %}
          {{ ['Please select...'] + ns.opts }}

# Script 2: Save all 4 manual RFID slots + reload
wallbox_update_vehicles:
  alias: "Update Wallbox Vehicles & Data"
  icon: mdi:content-save-all
  mode: single
  sequence:
    - action: shell_command.wallbox_write_vehicles
    - action: shell_command.wallbox_fetch_sessions
    - delay: "00:00:20"
    - action: homeassistant.update_entity
      target:
        entity_id: sensor.wallbox_sessions
    - delay: "00:00:04"
    - action: input_select.set_options
      target:
        entity_id: input_select.wallbox_month_filter
      data:
        options: >
          {{ ['All'] + ((state_attr('sensor.wallbox_sessions', 'monthly_summary') or []) | map(attribute='month_label') | list) }}
    - action: input_select.set_options
      target:
        entity_id: input_select.wallbox_rfid_selector
      data:
        options: >
          {% set sessions = state_attr('sensor.wallbox_sessions', 'sessions') %}
          {% set ns = namespace(seen=[], opts=[]) %}
          {% if sessions %}{% for s in sessions %}{% if s.rfid and s.rfid not in ns.seen %}{% set ns.seen = ns.seen + [s.rfid] %}{% set ns.opts = ns.opts + [s.rfid ~ ' — ' ~ s.vehicle] %}{% endif %}{% endfor %}{% endif %}
          {{ ['Please select...'] + ns.opts }}
```

### 5. Install HACS Card (if not already present)

The dashboard requires **apexcharts-card** (HACS → Frontend):
- HACS → Frontend → install `apexcharts-card` by RomRider
- Tested with version **2.2.3**

### 6. Add the dashboard to the sidebar

The wallbox dashboard is a dedicated dashboard with the URL **`dashboard-wallbox`** and four tabs.
It has to be registered in Home Assistant first — only then does it appear in the sidebar on the
left, and only then can it be filled with content.

#### 6.1 Register the dashboard (web interface)

1. Open **Settings → Dashboards**
2. Click **"+ Add dashboard"** at the bottom right
3. Choose **"New dashboard from scratch"**
4. Fill in the fields:

   | Field | Value |
   |---|---|
   | **Title** | `Wallbox` — this text appears in the sidebar |
   | **Icon** | `mdi:ev-station` |
   | **URL** | `dashboard-wallbox` |
   | **Show in sidebar** | enabled |
   | **Admin only** | disabled |

5. Click **"Create"**

> **The URL must contain a hyphen.** Home Assistant rejects `wallbox` or `dashboard_wallbox`
> with the message *"Url path needs to contain a hyphen (-)"*. Enter exactly `dashboard-wallbox` —
> every link in this documentation and the start-page references assume this URL.

The dashboard now shows up in the sidebar, but it is still empty.

#### 6.2 Add content — option A: raw configuration editor (recommended)

The dashboard definitions **ship with the integration**. After the HACS install they are located on
the Home Assistant host at `/config/custom_components/mennekes_amtron/dashboards/`. There are **two
variants** — both with the same four tabs and the same URLs:

| File | Use | Requires |
|---|---|---|
| [`wallbox_dashboard_integration.yaml`](custom_components/mennekes_amtron/dashboards/wallbox_dashboard_integration.yaml) | **Recommended for a fresh install.** Mapped exclusively to the entities the integration creates (`sensor.mennekes_amtron_*`, `number.*`, `switch.*`) | only the integration |
| [`wallbox_dashboard.yaml`](custom_components/mennekes_amtron/dashboards/wallbox_dashboard.yaml) | Full version with system-event filters, DLM cards and vehicle mapping | integration **plus** the template sensors, helpers and scripts of the YAML part (steps 1–4) |

> **If you install only the integration via HACS, use `wallbox_dashboard_integration.yaml`.** That
> variant references only entities the integration itself creates — no card shows "entity not
> found". The full version requires the complete YAML part and stays largely empty without it.

No restart needed, works without file access to `/config`:

1. Open the new **Wallbox** dashboard from the sidebar
2. Click the **pencil icon** (edit) at the top right
3. Click the **three-dot menu ⋮ → "Raw configuration editor"** at the top right
4. Paste the **entire contents** of the chosen file, replacing the existing text completely — it
   already contains all four tabs
5. **Save**, then close the editor

With file access you can skip the detour through the browser:

```bash
cat /config/custom_components/mennekes_amtron/dashboards/wallbox_dashboard_integration.yaml
```

You can switch between the variants at any time: just paste the other file's contents into the raw
configuration editor. The dashboard entry and the URLs stay unchanged.

#### 6.3 Add content — option B: write the storage file

For scripted installs with file access to `/config`. Requires step 6.1 to be done, otherwise there
is no dashboard the file belongs to.

The same shipped YAML file is wrapped into Home Assistant's storage format — the result is
identical to option A:

```bash
python3 - <<'EOF'
import json
import yaml

# Pick a variant: wallbox_dashboard_integration.yaml (integration only)
#                 or wallbox_dashboard.yaml (full version with the YAML part)
SRC = "/config/custom_components/mennekes_amtron/dashboards/wallbox_dashboard_integration.yaml"
DST = "/config/.storage/lovelace.dashboard_wallbox"

with open(SRC) as f:
    config = yaml.safe_load(f)

with open(DST, "w") as f:
    json.dump({"version": 1, "minor_version": 1,
               "key": "lovelace.dashboard_wallbox",
               "data": {"config": config}},
              f, ensure_ascii=False, indent=2)

print(f"{len(config['views'])} tabs written to {DST}")
EOF

# Restart HA: Settings → System → Restart
```

The file name is not arbitrary: Home Assistant derives it from the URL —
`dashboard-wallbox` → `.storage/lovelace.dashboard_wallbox`. With a different URL the file is
ignored.

#### 6.4 Verify the result

After either option these four tabs are reachable:

| Tab | URL | Content |
|---|---|---|
| Overview | `/dashboard-wallbox/wallbox-main` | Status, current session, energy, power, voltage & current, read-only limits, DLM |
| History | `/dashboard-wallbox/wallbox-history` | ApexCharts bar chart, monthly table, session list |
| System events | `/dashboard-wallbox/wallbox-systemlogs` | Wallbox event list with date, event ID, level and text filters |
| Configuration | `/dashboard-wallbox/wallbox-config` | Vehicle mapping, electricity price, safe current, HEMS limit, RFID slots |

The URLs can be opened directly in the browser and work as targets for buttons or `navigate`
actions in other dashboards.

> **Mind the order:** without step 6.1 there is no sidebar entry, and the file from step 6.3 has no
> effect.

#### 6.5 Configure the tabs — prerequisites per tab

##### Variant `wallbox_dashboard_integration.yaml`

No preparation needed — every card reads entities of the integration. What the tabs show:

| Tab | Content | Data source |
|---|---|---|
| **Overview** | Status, current or last charging session, energy, power, voltage & current, read-only limits | Modbus registers, every 30 s |
| **History** | Totals plus monthly, per-vehicle and session tables | the `monthly_summary`, `vehicle_totals` and `sessions` attributes of `sensor.mennekes_amtron_sessions_summary` (REST API, hourly) |
| **System events** | A note on how to activate the tab with the optional sensors from [`SYSTEMLOGS_SETUP.md`](SYSTEMLOGS_SETUP.md) | – |
| **Configuration** | HEMS limit, safe current, communication timeout, charging pause, availability | the integration's `number.*` and `switch.*` entities |

With this variant the electricity price and the update interval are not maintained through helpers
but via **Settings → Devices & Services → Mennekes AMTRON → Configure**.

Two limitations of the integration affect the cards: the **availability** switch writes to register
124, which is documented as read-only (see [Known Limitations](#known-limitations)), and the
integration does not provide **Dynamic Load Management** — those cards exist only in the full
version.

##### Variant `wallbox_dashboard.yaml` (full version)

The full version is the unmodified export of a running installation. It references three groups of
entities; if a group is missing, only the affected cards stay empty.

| Tab | Requires | Source |
|---|---|---|
| **Overview** | `sensor.wallbox_*`, `sensor.meter_*`, `sensor.vehicle_state`, `sensor.dlm_*`, `input_boolean.wallbox_*`, `input_number.wallbox_*` | template sensors from `templates/wallbox.yaml` and helpers from the `input_*_wallbox.yaml` files (steps 2–4) |
| **Overview**, "current session" card | `sensor.kessi_battery`, `sensor.tessi_battery`, `sensor.kessi_time_charge_complete`, `sensor.tessi_time_charge_complete` | **installation-specific** — see "Adapting the vehicle cards" below |
| **History** | `sensor.wallbox_sessions`, `sensor.wallbox_kosten_*`, `sensor.wallbox_kwh_*`, `input_select.wallbox_month_filter` | template sensors + fetch script (step 3) |
| **History** | `custom:apexcharts-card` | HACS → Frontend (step 5) |
| **System events** | `sensor.wallbox_system_events`, `script.wallbox_refresh_system_events` | [`SYSTEMLOGS_SETUP.md`](SYSTEMLOGS_SETUP.md) |
| **System events** | 5 filter helpers `input_datetime.systemevents_*`, `input_select.systemevents_*`, `input_text.systemevents_search` | see the YAML block below |
| **Configuration** | `input_text.wallbox_vehicle_1..4_*`, `input_select.wallbox_rfid_selector`, `script.wallbox_zuweise_fahrzeug`, `script.wallbox_aktualisiere_fahrzeuge` | helpers + scripts (steps 2–4) |

**Filter helpers for the System events tab** — add to `configuration.yaml` (or to the existing
`input_*_wallbox.yaml` files if they are pulled in via `!include`):

```yaml
input_datetime:
  systemevents_date_from:
    name: Systemereignisse Von
    has_date: true
    has_time: false
    icon: mdi:calendar-start
  systemevents_date_to:
    name: Systemereignisse Bis
    has_date: true
    has_time: false
    icon: mdi:calendar-end

input_select:
  systemevents_level:
    name: Level Filter (Systemereignisse)
    icon: mdi:alert-circle-outline
    options:
      - Alle
      - Information
      - Error
  systemevents_event_id:
    name: Event-ID Filter
    icon: mdi:tag-outline
    # initial value; the fetch script fills the list with the IDs that actually occur
    options:
      - Alle

input_text:
  systemevents_search:
    name: Kurzbeschreibung Suche
    max: 50
    mode: text
    icon: mdi:magnify
```

**Adapting the vehicle cards.** The Overview tab shows the state of charge of the two vehicles of
the reference installation in two `conditional` cards. Those sensors come from a Tesla integration
and are named after the vehicle names used there:

| Placeholder in the dashboard | Replace with |
|---|---|
| `sensor.kessi_battery`, `sensor.tessi_battery` | state-of-charge sensor of your own vehicle (`device_class: battery`) |
| `sensor.kessi_time_charge_complete`, `sensor.tessi_time_charge_complete` | "charge complete at" sensor of your own vehicle |
| Labels `Kessi` / `Tessi` | your own vehicle names |

Without your own vehicle integration, both `conditional` cards can simply be deleted in the raw
configuration editor — the remaining cards of the tab are unaffected. The vehicle names used for
**cost allocation**, by contrast, are maintained via the Configuration tab, not in the dashboard
(see [Managing vehicles](#managing-vehicles-rfid--name)).

> **Entity namespaces:** the shipped dashboard uses the template sensors of the YAML part
> (`sensor.wallbox_*`, `sensor.meter_*`). The integration itself creates its entities under
> `sensor.mennekes_amtron_*`. For an installation **without** the YAML part, the entity IDs have to
> be replaced accordingly in the raw configuration editor — the mapping is in
> [All HA entities](#all-ha-entities).

After restart, the startup automation runs automatically:
- Charging sessions are fetched from the API (~20s)
- `sensor.wallbox_sessions` is updated
- RFID dropdown is populated with known vehicles
- Month filter dropdown receives all available months

---

## Dashboard – Tab Description

The wallbox dashboard is accessible at `/dashboard-wallbox/` and has four tabs. See
[Add the dashboard to the sidebar](#6-add-the-dashboard-to-the-sidebar) for how to create it.

### Tab 1: Overview

Real-time monitoring via Modbus TCP (updated every 30 seconds):

| Card | Content |
|------|---------|
| **Status** | Charging status, vehicle state, availability, plug lock, error codes, protocol version |
| **Current Charging Session** | Session energy, charge duration, signaled current, max. vehicle current |
| **Energy (kWh)** | Total energy + L1/L2/L3 individually |
| **Power (W)** | Total power + L1/L2/L3 individually |
| **Voltage & Current** | Voltage and current per phase |
| **Limits (read)** | HEMS current limit, operator limit, safe current, timeout – display only |
| **Dynamic Load Management** | DLM mode, slaves, available/applied current L1-L3 |

### Tab 2: History

Charging sessions from the REST API – panel view (full width):

```
┌──────────────────┬─────────────────────────────────────────┐
│ Statistics &     │  ApexCharts Bar Chart                    │
│ Filter (1/3)     │  Monthly consumption per vehicle (2/3)   │
├──────────────────┴─────────────────────────────────────────┤
│  Monthly table (kWh & CHF) – full width                     │
├─────────────────────────────────────────────────────────────┤
│  Charging sessions table – full width                        │
└─────────────────────────────────────────────────────────────┘
```

#### Statistics & Filter (left column, 1/3)

Shows overall summary and month filter:
- Number of charging sessions
- Total energy / total costs CHF
- Vehicle 1 total / Vehicle 2 total
- kWh & costs current month
- **Month filter dropdown** (`input_select.wallbox_month_filter`): Select a month → charging sessions table filters automatically

#### ApexCharts Bar Chart (right column, 2/3)

Stacked bar chart with one bar per month, broken down by vehicle (blue = vehicle 1, orange = vehicle 2).

**How it works:**
- Reads directly from `sensor.wallbox_sessions` → attribute `monthly_summary` via JavaScript `data_generator`
- **No HA statistics or long-term storage required** – all historical months from the session JSON are displayed immediately
- Time window: `graph_span: 13month` (last 13 months visible)
- New months appear automatically on the next hourly fetch

**Prerequisites:**
- apexcharts-card (HACS) installed, version ≥ 2.2.3
- `sensor.wallbox_sessions` must be excluded from the recorder (prevents freeze on the History API)

#### Monthly Table (full width)

Table of all months with exact kWh and CHF values:

| Month | Vehicle 1 kWh | CHF | Vehicle 2 kWh | CHF | Total kWh | CHF |
|-------|---------------|-----|---------------|-----|-----------|-----|
| May 2026 | 298.1 | 86.44 | 0.0 | 0.00 | 298.1 | 86.44 |
| April 2026 | 5.2 | 1.50 | 39.7 | 11.51 | 44.9 | 13.01 |

- Price comes from `input_number.wallbox_price_per_kwh` (adjustable live)
- Most recent months at the top

#### Charging Sessions Table (full width)

All charging sessions with date, vehicle, duration, kWh and CHF.

- Filtered by the month filter
- With "All": shows vehicle totals at the bottom
- With month selection: shows monthly totals per vehicle

### Tab 3: System events

`/dashboard-wallbox/wallbox-systemlogs` — the wallbox event log for troubleshooting, with a filter
bar spread over three cards.

| Card | Content |
|------|---------|
| **Status** | `sensor.wallbox_system_events` (entry count), `sensor.wallbox_software_version` (firmware) and a "Refresh" button that triggers `script.wallbox_refresh_system_events` |
| **Date** | `input_datetime.systemevents_date_from` / `…_date_to` — limits the evaluated period |
| **Filter** | `input_select.systemevents_event_id` (event ID), `input_select.systemevents_level` (Information / Error / All), `input_text.systemevents_search` (free text in the short description) |
| **System events** | Markdown table of the filtered events from the `events` attribute |

The filters act on the display only: the markdown card evaluates the four helpers against the
events stored in the sensor attribute on every page load. Data is fetched from the wallbox again
only via the button or the hourly automation.

Prerequisites: the command-line sensors and Python scripts from
[`SYSTEMLOGS_SETUP.md`](SYSTEMLOGS_SETUP.md) plus the five filter helpers from
[Configure the tabs](#65-configure-the-tabs--prerequisites-per-tab). Without them this tab stays
empty — the other three are unaffected.

### Tab 4: Configuration

All settings and vehicle management in one place.

#### Card: Assign Vehicle (Dropdown Method, Recommended)

The most convenient way to assign a vehicle name to an RFID tag:

1. **Select RFID** from the dropdown (`input_select.wallbox_rfid_selector`)
   - Format: `04A5F3D2CC1D90 — Kessi`
   - Automatically populated with all known RFIDs after each fetch
   - Shows the currently stored name (or "Unknown" if new)
2. **Enter new vehicle name** (`input_text.wallbox_vehicle_name_new`)
3. Press **"Assign & Reload Data"** button
   - Calls `script.wallbox_assign_vehicle`
   - Saves RFID → name in `wallbox_vehicles.json`
   - Re-fetches all sessions with the updated mapping
   - Updates both dropdowns

#### Card: Known Vehicles

Table of all RFIDs with their current name (determined from charging sessions).

#### Card: Wallbox Settings

All configuration parameters:

| Entity | Description |
|--------|-------------|
| `input_number.wallbox_price_per_kwh` | Electricity price CHF/kWh – changes all cost calculations immediately |
| `input_number.wallbox_hems_current_limit` | HEMS current limit (0 = pause, 6-16A) |
| `input_number.wallbox_safe_current` | Safe current (0-32A) |
| `input_number.wallbox_comm_timeout` | Communication timeout (1-300s) |
| `input_boolean.wallbox_cp_availability` | CP availability on/off |
| `input_boolean.wallbox_pause_charging` | Pause charging immediately |

#### Card: Manual RFID Management (4 Slots)

Older method with fixed slots for 4 vehicles. Button "Save all 4 slots & reload" writes all 4 entries to `wallbox_vehicles.json` at once.

---

## Configuration Files

### `wallbox_config.json` – Electricity Price for Fetch

```json
{
  "price_per_kwh_chf": 0.29
}
```

This price is embedded into session data by the fetch script. In the dashboard, the price can be adjusted live via `input_number.wallbox_price_per_kwh` – this takes effect immediately on all displays without a new fetch.

### `wallbox_vehicles.json` – RFID Mapping

```json
{
  "04A5F3D2CC1D90": "Kessi",
  "049D869A5A2294": "Tessi"
}
```

Read by `fetch_charging_sessions.py` to assign vehicle names to sessions. Can be edited via the dashboard (Configuration tab) or directly.

---

## How Is the Price Calculated?

The electricity price is configured in **two stages**:

1. **`wallbox_config.json`** (`price_per_kwh_chf: 0.29`) – read during fetch and embedded in `wallbox_sessions.json`
2. **`input_number.wallbox_price_per_kwh`** (default: 0.29) – live value for HA template sensors and dashboard

**Cost calculation**: `energy_kwh × price_per_kwh`

| Change... | Effect |
|-----------|--------|
| `input_number.wallbox_price_per_kwh` in dashboard | All cost displays update **immediately** (live) |
| Edit `wallbox_config.json` directly | Takes effect on the next fetch (hourly) on JSON data |

---

## When / How Is Data Updated?

### Automatically

| Time | What happens |
|------|-------------|
| HA start | Fetch automation starts, retrieves all sessions from API |
| Every full hour (`:00`) | Automation fetches sessions, updates sensor + both dropdowns |
| Every 30 seconds | Modbus polling: voltage, current, power, status |
| Every 60 minutes | Modbus: software version, total energy counter |

### Manually (Developer Tools → Services)

```yaml
# Trigger session fetch manually:
service: shell_command.wallbox_fetch_sessions

# Read sensor immediately:
service: homeassistant.update_entity
entity_id: sensor.wallbox_sessions

# Assign vehicle (use dropdown value):
service: script.wallbox_assign_vehicle

# Save all 4 slots + reload:
service: script.wallbox_update_vehicles
```

### Fetch Flow

```
Automation trigger (start or /1h)
    │
    ├── shell_command.wallbox_fetch_sessions
    │       └── run_wallbox_fetch.sh
    │               └── fetch_charging_sessions.py
    │                       ├── GET /api/v1/Nonce
    │                       ├── POST /api/v1/AuthManagement/login (Installer)
    │                       ├── GET /api/v1/ChargingTransactionHistory/ReadFromTo
    │                       │       from=2024-01-01, take=100, sorted in Python
    │                       ├── RFID → name via wallbox_vehicles.json
    │                       ├── cost calculation via wallbox_config.json
    │                       └── writes /config/wallbox_sessions.json
    │
    ├── homeassistant.update_entity(sensor.wallbox_sessions)
    │       └── cat /config/wallbox_sessions.json → sensor state + attributes
    │
    ├── delay 4s
    │
    ├── input_select.set_options(wallbox_month_filter)
    │       └── ['All', 'May 2026', 'April 2026', ...]
    │
    └── input_select.set_options(wallbox_rfid_selector)
            └── ['Please select...', '04A5F3D2CC1D90 — Kessi', '049D869A5A2294 — Tessi']
```

---

## Managing Vehicles (RFID → Name)

### Method 1: Dropdown (Recommended)

1. Dashboard → Tab **"Configuration"**
2. **"Select RFID"** – dropdown shows all known RFIDs with current name
3. **"New vehicle name"** – enter name (e.g. "Kessi")
4. Press **"Assign & Reload Data"**
5. After ~25 seconds: sessions show the new name, dropdown updated

### Method 2: Manual 4-Slot Management

1. Dashboard → Tab **"Configuration"** → Card "Manual RFID Management"
2. Enter RFID IDs and names in the fields
3. Press **"Save all 4 slots & reload"**

### Method 3: Directly via File

```bash
# SSH to NAS:
nano /volume1/docker/homeassistant/wallbox_vehicles.json

# Format:
{
  "04A5F3D2CC1D90": "Kessi",
  "049D869A5A2294": "Tessi",
  "NEW_RFID_ID": "New Vehicle"
}
```

Then trigger: `service: shell_command.wallbox_fetch_sessions`.

### Where Does the RFID Come From?

RFIDs appear automatically in:
- **Configuration tab** → "Known Vehicles" (from charging sessions)
- **RFID dropdown** (`wallbox_rfid_selector`) – updated after each fetch

Unknown RFIDs appear as `"RFID_CODE — RFID_CODE"` (RFID = name, not yet assigned).

---

## All HA Entities

### Modbus Sensors (directly from wallbox via Modbus)

| Entity | Description | Unit |
|--------|-------------|------|
| `sensor.meter_voltage_l1/l2/l3` | Voltage per phase | V |
| `sensor.wallbox_current_l1/l2/l3_ampere` | Current per phase | A |
| `sensor.meter_power_l1/l2/l3` | Power per phase | W |
| `sensor.wallbox_total_power` | Total power | W |
| `sensor.wallbox_energy_l1/l2/l3_kwh` | Energy per phase | kWh |
| `sensor.wallbox_total_energy_kwh` | Total energy | kWh |
| `sensor.wallbox_session_energy_kwh` | Session energy | kWh |
| `sensor.hems_current_limit` | HEMS limit (read) | A |
| `sensor.operator_current_limit` | Operator limit | A |
| `sensor.safe_current` | Safe current | A |
| `sensor.comm_timeout` | Timeout | s |
| `sensor.signaled_current` | Signaled current | A |
| `sensor.max_current_ev` | Max. EV current | A |
| `sensor.dlm_num_slaves_connected` | DLM slaves | – |
| `sensor.dlm_overall_current_available_l1/l2/l3` | DLM available | A |
| `sensor.dlm_overall_current_applied_l1/l2/l3` | DLM applied | A |

### Template Sensors (from `templates/wallbox.yaml`)

| Entity | Description |
|--------|-------------|
| `sensor.wallbox_charging_status` | Charging status (text: Charging, Ready, …) |
| `sensor.wallbox_vehicle_state_text` | Vehicle state A-E |
| `sensor.wallbox_cp_availability_text` | Availability |
| `sensor.wallbox_plug_lock_status_text` | Plug lock status |
| `sensor.wallbox_error_codes_text` | Error codes decoded |
| `sensor.wallbox_dlm_mode_text` | DLM mode text |
| `sensor.wallbox_charge_duration_formatted` | Charge duration hh:mm:ss |
| `sensor.wallbox_chargepoint_model` | Model string |

### Cost Sensors (from `templates/wallbox.yaml`)

| Entity | Description |
|--------|-------------|
| `sensor.wallbox_total_cost_chf` | Total costs CHF |
| `sensor.wallbox_kwh_current_month` | kWh in current month |
| `sensor.wallbox_cost_current_month_chf` | Costs in current month CHF |
| `sensor.wallbox_kwh_vehicle1_total` | Vehicle 1 total consumption kWh |
| `sensor.wallbox_kwh_vehicle2_total` | Vehicle 2 total consumption kWh |

### Sessions Sensor (`command_line`)

| Entity / Attribute | Description |
|-------------------|-------------|
| `sensor.wallbox_sessions` (state) | Number of charging sessions |
| `.attributes.sessions` | List of all sessions (max. 100) |
| `.attributes.monthly_summary` | Monthly summary with `by_vehicle` |
| `.attributes.vehicle_totals` | Total consumption per vehicle |
| `.attributes.total_kwh` | Total energy of all sessions |
| `.attributes.vehicles` | List of all vehicle names |
| `.attributes.last_session_kwh` | Last session kWh |
| `.attributes.last_vehicle` | Last vehicle |

> **Recorder exclusion**: `sensor.wallbox_sessions` is excluded from the HA recorder (`recorder: exclude`). Data is persisted in `wallbox_sessions.json`. No History tab in HA for this entity.

### Helper Entities

| Entity | Description |
|--------|-------------|
| `input_number.wallbox_price_per_kwh` | Electricity price CHF/kWh (live, 0.01–2.00) |
| `input_number.wallbox_hems_current_limit` | HEMS limit setting (0-16A) |
| `input_number.wallbox_safe_current` | Safe current setting (0-32A) |
| `input_number.wallbox_comm_timeout` | Comm timeout setting (1-300s) |
| `input_boolean.wallbox_cp_availability` | CP availability |
| `input_boolean.wallbox_pause_charging` | Pause charging |
| `input_select.wallbox_month_filter` | Month filter (auto-populated after fetch) |
| `input_select.wallbox_rfid_selector` | RFID dropdown for vehicle assignment (auto-populated) |
| `input_text.wallbox_vehicle_1-4_rfid` | RFID card slots (manual method) |
| `input_text.wallbox_vehicle_1-4_name` | Vehicle name slots (manual method) |
| `input_text.wallbox_vehicle_name_new` | New name for dropdown assignment |

---

## API Authentication (Wallbox REST)

```
1. GET  /api/v1/Nonce?nocache=<timestamp>        → Nonce string
2. POST /api/v1/AuthManagement/login              → Bearer token
   Header: X-Nonce: <nonce>
   Body:   {"username": "Installer", "password": "<password>"}
3. GET  /api/v1/ChargingTransactionHistory/ReadFromTo
   Header: Authorization: Bearer <token>
   Params: skip=0&take=100&from=2024-01-01T00:00:00.000Z&to=<now>
```

**Important API pitfalls:**

| Problem | Cause | Solution |
|---------|-------|----------|
| HTTP 400 on login | Wrong username | Must be exactly `"Installer"` (capital I) |
| HTTP 400 on history | `orderBy` parameter | Remove parameter, sort in Python |
| Timeout on history | `from=2020-01-01` | Always use `from=2024-01-01` – 2020 has test sessions |
| Password error | Special characters | Always use single quotes in shell: `'...'` |

### Password

The wallbox password is stored in `/config/python_scripts/run_wallbox_fetch.sh`:
```sh
#!/bin/sh
WALLBOX_PASS='<your-password>' python3 /config/python_scripts/fetch_charging_sessions.py > /config/wallbox_fetch.log 2>&1
```

---

## Modbus Register Reference

Source: `_documents/AMTRON-4You500-4Business700-Modbus-TCP-Register-v1.5.pdf`
(protocol version 1.5, firmware level 1.5.21). All registers are holding registers,
server on port 502, unit ID 1.

> **Important note on word order:** every `int32`/`uint32` value occupies **two** registers,
> high word first. Consecutive phases are therefore 2 registers apart. Reading only the first
> register yields a constant 0 for power and voltage, because realistic values fit entirely
> into the low word.

### Read (FC03)

| Register | Description | Type / Unit |
|----------|-------------|-------------|
| 100–101 | Firmware version | 4 × ASCII |
| 104 | OCPP status | uint16, 0–9 |
| 105–112 | Error codes | 4 × uint32 (bitmask) |
| 120–121 | Protocol version | 4 × ASCII |
| 122 | Vehicle state | int16, 1–5 (A–E) |
| 124 | Charge point availability | uint16, 0 = unavailable, 1 = available |
| 134 | Operator current limit | uint16 [A] |
| 140 | Relay state | uint16, 0 = off, 1 = on |
| 141 | Device id | 2 × ASCII (always `AM`) |
| 142–151 | Charge point model | 20 × ASCII |
| 152 | Plug lock status | uint16, 0–4 |
| 153–157 | Firmware versions | major, minor, patch (uint16), build (uint32) |
| 200–205 | Meter energy L1/L2/L3 | 3 × int32 [Wh] — L1 = meter total, L2/L3 = 0 |
| 206–211 | Meter power L1/L2/L3 | 3 × int32 [W] |
| 212–217 | Meter current L1/L2/L3 | 3 × int32 [mA] |
| 218–219 | Meter total energy | int32 [Wh] |
| 220–221 | Meter total power | int32 [W] |
| 222–227 | Meter voltage L1/L2/L3 | 3 × int32 [V] |
| 600 | Charging point network mode | uint16, 0 / 1 / 4 |
| 610–612 | CPN current limit | 3 × uint16 [A] |
| 620 | CPN source of limitation | uint16, 0–5 |
| 621 | CPN connected charging stations | uint16 |
| 630–632 | CPN overall current applied | 3 × uint16 [A] |
| 633–635 | CPN overall current available | 3 × uint16 [A] |
| 706 | Signaled current to EV | uint16 [A] |
| 707–708 | Charging start time | BCD `hhmmss` |
| 710–711 | Charging end time | BCD `hhmmss` |
| 712 | Min charging current limit | uint16 [A] |
| 715 | Max charging current limit | uint16 [A] |
| 716–717 | Charged energy (session) | uint32 [Wh] |
| 718–719 | Charging duration | uint32 [s] |
| 2010 | Modbus TCP / HEMS configuration | uint16, 0 = inactive, 1 = read only, 2 = read/write |
| 2011 | HEMS communication status | uint16, 0 = ok, 1 = timeout (safe current active) |
| 2012 | HEMS power limit (minimum) | uint16 [W] |
| 2013 | HEMS power limit (maximum) | uint16 [W] |
| 2020 | Phase switch mode | uint16, 0–3 |
| 2021 | Phase switch pause | uint16 [s] |
| 2022 | Phase switch status | uint16, 0 / 1 |
| 2023 | Assigned phases | uint16, 0 = none, 1 = one phase, 2 = three phases |
| 2030 | Authorization status | uint16, 0 = autostart, 1 = authorized, 2 = not authorized |
| 2158–2173 | Device name | 32 × ASCII |
| 2622 | CPN satellites in fallback | uint16 |
| 2623 | CPN satellite fallback current | uint16 [A] |
| 2636–2638 | CPN overall current consumption | 3 × uint16 [A] |

### Write (FC06 / FC16)

Requires register 2010 to report `2` (Modbus TCP in read-and-write mode).

| Register | Description | Range |
|----------|-------------|-------|
| 131 | Safe current | 0 A (pause) or 6–16 A; values below 6 A become 0 A |
| 132 | Communication timeout | uint16 [s] — register 131 applies afterwards |
| 613–615 | CPN EMS current limit L1/L2/L3 | 3 × uint16 [A]; the lowest value applies to all phases |
| 2000 | HEMS current limit | 0 A (pause) or 6–16 A |
| 2001 | HEMS current limit in 0.1 A | 0 or 60–160 |
| 2002 | HEMS power limit | 0 W (pause), otherwise between registers 2012 and 2013 |
| 1000 / 1001 / 1002 | HEMS limits, legacy addresses | 1000 is a copy of 2000; 1001 and 1002 are **deprecated** → 2001 / 2002 |

**Not writable:** register 124 (charge point availability) is read-only in protocol version 1.5 —
see Known Limitations.

---

## Fallback: Mobile Network Access

If the wallbox is not reachable via WiFi:
- **Mobile IP**: `10.x.x.x` (GSM backup, via SIM card) — if available

Change the `host` in `modbus_wallbox.yaml`:
```yaml
hub:
  - name: "Mennekes AMTRON Wallbox"
    host: 10.x.x.x  # ← fallback IP, replace with the actual IP
    port: 502
```

Or use environment variables in `.env`:
```bash
WALLBOX_URL=http://10.x.x.x/api/v1
```

---

## Troubleshooting

### History Page Freezes the Browser

**Cause**: `sensor.wallbox_sessions` is not excluded from the recorder. apexcharts-card loads the complete entity history when opened (hourly updates × large JSON attributes = MB of data).

**Fix**: Exclude the sensor in `configuration.yaml` under `recorder:`:
```yaml
recorder:
  exclude:
    entities:
      - sensor.wallbox_sessions
```
Then restart HA.

### ApexCharts Shows Empty Chart / No Bars

Possible causes:
1. `apexcharts-card` not installed (HACS → Frontend)
2. `sensor.wallbox_sessions` has no data yet → wait for fetch to complete
3. Wrong chart type: must be `type: column` on the series (not `chart_type: bar` at card level – not supported in v2.2.3)
4. `graph_span` missing → data outside the visible time window

### ApexCharts Shows "Configuration Error"

`apexcharts-card v2.2.3` only supports `chart_type: line/scatter/pie/donut/radialBar` at card level. For bars: set `type: column` on each series, no `chart_type: bar`.

### sensor.wallbox_sessions Shows 0 or Doesn't Appear

```bash
# Check JSON file
cat /volume1/docker/homeassistant/wallbox_sessions.json | python3 -m json.tool

# View fetch log
cat /volume1/docker/homeassistant/wallbox_fetch.log

# Check sensor format: must be top-level command_line
# CORRECT:
command_line:
  - sensor:
      name: "Wallbox Sessions"
# WRONG (deprecated since HA 2022.11):
sensor:
  - platform: command_line
```

### Sessions Show "Unknown" as Vehicle

1. Dashboard → Tab "Configuration" → "Known Vehicles"
2. Read RFID from table
3. Select the corresponding RFID in the "Select RFID" dropdown
4. Enter name → press "Assign & Reload Data"

### Wallbox Not Reachable

```bash
# Check WiFi connection (replace 192.x.x.x with your wallbox IP)
ping 192.x.x.x
curl -sf http://192.x.x.x/api/v1/PublicInfo

# Check Modbus port
nc -zv 192.x.x.x 502

# Try GSM fallback (if configured, replace 10.x.x.x)
ping 10.x.x.x
```

### Wallbox API Returns HTTP 400

- Username must be exactly `"Installer"` (capital I)
- Remove `orderBy` parameter
- Use `from=2024-01-01` (not 2020 → timeout from test sessions)

---

## Known RFID Cards

| RFID | Vehicle |
|------|---------|
| `04A5F3D2CC1D90` | Kessi (Tesla) |
| `049D869A5A2294` | Tessi (Tesla) |

---

## File Overview

```
/workspace/HA_Menneckes/                    (source code / development)
├── README.md                               ← quick start (German)
├── README.en.md                            ← quick start (English)
├── INSTALLATION_MANUELL.md                 ← manual installation (German)
├── INSTALLATION_MANUAL.md                  ← this file
├── generate_dashboard.py                   ← superseded, see "Pushing dashboard changes back"
├── modbus_wallbox.yaml                     ← Modbus TCP register map
├── input_number_wallbox.yaml               ← Numeric input helpers
├── input_boolean_wallbox.yaml              ← Boolean input helpers
├── input_select_wallbox.yaml               ← Dropdown helpers (month, RFID)
├── input_text_wallbox.yaml                 ← Text helpers (vehicle names, RFIDs)
├── templates/
│   └── wallbox.yaml                        ← Template sensors
├── custom_components/mennekes_amtron/
│   ├── ...                                 ← integration (installed by HACS)
│   └── dashboards/
│       └── wallbox_dashboard.yaml          ← dashboard raw configuration, 4 tabs (source)
├── dashboards/
│   └── wallbox_dashboard.yaml              ← identical copy of the file above
├── python_scripts/
│   ├── fetch_charging_sessions.py          ← REST API fetch (main script)
│   ├── run_wallbox_fetch.sh                ← Wrapper (password not in repo)
│   ├── write_vehicles.py                   ← Writes vehicles.json (4-slot method)
│   └── assign_vehicle.py                   ← Writes vehicles.json (dropdown method)
├── VERSION
├── LICENSE
└── .gitignore

/workspace/homeassistant/                   (HA config, live = /config/ in container)
├── configuration.yaml                      ← Main config (recorder, command_line, shell_command)
├── automations.yaml                        ← Wallbox fetch automation
├── scripts.yaml                            ← wallbox_assign_vehicle + wallbox_update_vehicles
├── modbus_wallbox.yaml
├── input_number_wallbox.yaml
├── input_boolean_wallbox.yaml
├── input_select_wallbox.yaml               ← wallbox_month_filter + wallbox_rfid_selector
├── input_text_wallbox.yaml                 ← vehicle_1-4 + vehicle_name_new
├── wallbox_config.json
├── wallbox_vehicles.json
├── wallbox_sessions.json                   ← Generated by fetch, do not edit manually
├── wallbox_fetch.log                       ← Fetch log (debug)
├── templates/
│   └── wallbox.yaml                        ← Template sensors + cost sensors
├── python_scripts/
│   ├── fetch_charging_sessions.py
│   ├── run_wallbox_fetch.sh
│   ├── write_vehicles.py
│   └── assign_vehicle.py
└── .storage/
    └── lovelace.dashboard_wallbox          ← Lovelace dashboard JSON
```

### Pushing dashboard changes back

The single source is the file shipped with the integration,
`custom_components/mennekes_amtron/dashboards/wallbox_dashboard.yaml`. Both insertion options from
step 6 read it; it holds the unmodified export of the production installation.

If you develop the dashboard further in the web interface, push the state back into the repository
like this:

1. Open the dashboard → pencil → ⋮ → **Raw configuration editor**
2. Copy the entire content
3. Paste it into `custom_components/mennekes_amtron/dashboards/wallbox_dashboard.yaml` below the
   comment header
4. Keep the copy in sync:
   ```bash
   cd /workspace/HA_Menneckes
   cp custom_components/mennekes_amtron/dashboards/wallbox_dashboard.yaml dashboards/
   ```

After option A no HA restart is needed, a `Shift`+`F5` in the browser is enough. After option B
Home Assistant has to be restarted, because the storage file is only read at startup.

> **`generate_dashboard.py` is superseded.** The script produced its own, older variant of the
> dashboard and is no longer the source of the shipped definition. It stays in the repository for
> now, but no installation step uses it any more.

---

## Version & Last Update

- **HA version**: 2026.5.4 (minimum: 2026.1.0)
- **Wallbox firmware**: 1.5.41 (tested)
- **apexcharts-card**: 2.2.3 (required for dashboard)
- **Python**: 3.9+ (already included in HA)
- **Last update**: 2026-06-24
- **Tested**: Modbus TCP ✓, REST API ✓, vehicle mapping (dropdown) ✓, cost calculation ✓, ApexCharts chart ✓, recorder exclusion ✓

---

## 📋 Known Limitations & Support

### Supported Wallboxes
- ✅ **AMTRON 4You 400/500** and **AMTRON 4Business 600/700** — identical register set,
  see [Supported models](#supported-models)
- ✅ Tested on **AMTRON 4Business 730 11 C2**, firmware 1.5.41
- ❌ Other Mennekes series (different or no Modbus register set)

### Known Limitations
1. **Modbus registers**: Based on protocol version 1.5 – newer versions may have different registers
2. **Write access**: Requires Modbus TCP in read-and-write mode (register 2010 = `2`).
   Register 124 (charge point availability) is documented as read-only — the availability
   switch cannot write to it.
3. **Maintenance state**: While the wallbox reports `systemStatus` `UpdateInProgress` via
   `GET /api/v1/Status`, it rejects every Modbus connection. Home Assistant then shows
   "Error setting up, retrying" and reconnects on its own once the state clears.
4. **REST API**: Requires installer password (not user password)
5. **Dashboard**: Requires `apexcharts-card` from HACS

### Troubleshooting

Before requesting support, please check:
1. **View logs**: Settings → System → Logs (search for "wallbox")
2. **Run diagnose.sh script**: `bash diagnose.sh`
3. **Read the [quick start](README.en.md) and this page** (comprehensive troubleshooting guides available)

---

## 🤝 Community & Support

- **GitHub Issues**: [nobelp/mennekes-amtron-ha/issues](https://github.com/nobelp/mennekes-amtron-ha/issues)
- **Home Assistant Community**: [Home Assistant Discourse](https://discourse.home-assistant.io)
- **Documentation**: [quick start](README.en.md), this page, [`SYSTEMLOGS_SETUP.md`](SYSTEMLOGS_SETUP.md)

---

## 📝 Changelog & Versioning

See [CHANGELOG.md](CHANGELOG.md) for complete change history.

**Versioning**: Semantic Versioning (MAJOR.MINOR.PATCH)
- `MAJOR`: Breaking changes
- `MINOR`: New features
- `PATCH`: Bug fixes

---

## 📜 License

MIT License – See [LICENSE](LICENSE) for details.

Copyright © 2026 nobelp
