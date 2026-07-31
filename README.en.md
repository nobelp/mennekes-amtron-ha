# Mennekes AMTRON Wallbox – Home Assistant Integration
### for AMTRON 4You 400 · 4You 500 · 4Business 600 · 4Business 700

[Deutsch (Schnellstart)](README.md) · [Manuelle Installation (Deutsch)](INSTALLATION_MANUELL.md) · **English (quick start)** · [Manual installation](INSTALLATION_MANUAL.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Release](https://img.shields.io/github/v/release/nobelp/mennekes-amtron-ha)](https://github.com/nobelp/mennekes-amtron-ha/releases)

Integrates a Mennekes AMTRON wallbox into Home Assistant — set up entirely through the web
interface, no YAML files required.

> **All AMTRON 4You 400 and 500 as well as 4Business 600 and 700 communicate identically.** They
> use the same Modbus TCP register set, so this integration's compatibility covers the entire
> portfolio — including sub-variants such as the 4Business 730 or the 4You 550.

Features:

- **Real-time monitoring** via Modbus TCP: charging status, voltage, current, power, energy
- **Charging history** via REST API: sessions, vehicle mapping, costs
- **Control**: HEMS limit, safe current, charging pause, availability
- **Dashboard** with four tabs, shipped with the integration

> This page describes the **automated path**: HACS, configuration dialog, paste the dashboard —
> done. If you also want template sensors, RFID-based vehicle mapping and system-event analysis,
> follow the [manual installation](INSTALLATION_MANUAL.md).

---

## Supported models

**AMTRON 4You 400/500** and **AMTRON 4Business 600/700** communicate identically — same Modbus TCP
register set on port 502, unit ID 1. The integration covers this entire portfolio, including
sub-variants such as the 4Business 730 or the 4You 550. Tested on an **AMTRON 4Business 730 11 C2**
with firmware 1.5.41.

Device requirement: protocol version **1.5** and Modbus TCP enabled. Register `2010` reports the
mode — `0` = off, `1` = read only, `2` = read and write. HEMS limit and safe current require `2`.

---

## Step 1: Install the integration

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nobelp&repository=mennekes-amtron-ha&category=integration)

1. Click the HACS button above, or in HACS add `https://github.com/nobelp/mennekes-amtron-ha` via
   **⋮ → Custom repositories** with category **Integration**
2. Search for **"Mennekes AMTRON"** and **download** it
3. **Restart** Home Assistant

---

## Step 2: Configure the wallbox

**Settings → Devices & Services → Add Integration → "Mennekes AMTRON"**

![Configuration dialog of the Mennekes AMTRON integration with fields for IP address, API port, installer password, Modbus port, electricity price and update interval](docs/images/config-flow-ui.png)

| Field | Meaning | Default |
|-------|---------|---------|
| **IP address or hostname** | Address of the wallbox on your network, e.g. `192.168.2.179` or `wallbox.local` | – (required) |
| **API port** | HTTP port used for the REST calls | `80` |
| **Installer password** | Password of the wallbox installer account | – (required) |
| **Modbus port** | TCP port of the Modbus protocol | `502` |
| **Electricity price (CHF/kWh)** | Basis for the cost calculation | `0.29` |
| **Update interval** | Interval of sensor updates in seconds (1–3600) | `30` |

After **OK** the integration creates one device with around 35 entities. It reads model, firmware
version and serial number from the wallbox itself — you do not need to select a model.

Electricity price and interval can be changed at any time via **Configure** on the integration
entry.

---

## Step 3: Set up the dashboard

The dashboard definition ships with the integration and is located after installation at
`/config/custom_components/mennekes_amtron/dashboards/`.

**3.1 Create the dashboard** — **Settings → Dashboards → "+ Add dashboard" →
"New dashboard from scratch"**:

| Field | Value |
|---|---|
| **Title** | `Wallbox` |
| **Icon** | `mdi:ev-station` |
| **URL** | `dashboard-wallbox` |
| **Show in sidebar** | enabled |

> The URL **must contain a hyphen** — Home Assistant rejects `wallbox` and `dashboard_wallbox` with
> *"Url path needs to contain a hyphen (-)"*.

**3.2 Insert the content** — open the new dashboard, top right **pencil → ⋮ →
"Raw configuration editor"**, replace the existing text entirely with the contents of this file and
save:

```
/config/custom_components/mennekes_amtron/dashboards/wallbox_dashboard_integration.yaml
```

This variant references only entities the integration creates, so no card shows "entity not found".
No restart required.

**Result:** four tabs.

| Tab | URL | Content |
|---|---|---|
| Overview | `/dashboard-wallbox/wallbox-main` | Status, current or last charging session, energy, power, voltage & current, read-only limits |
| History | `/dashboard-wallbox/wallbox-history` | Totals, monthly table, consumption per vehicle, recent sessions |
| System events | `/dashboard-wallbox/wallbox-systemlogs` | Note on the optional event analysis |
| Configuration | `/dashboard-wallbox/wallbox-config` | HEMS limit, safe current, timeout, charging pause, availability |

The second shipped file, `wallbox_dashboard.yaml`, is the **full version** with system-event
filters, DLM cards and vehicle mapping. It requires the
[manual installation](INSTALLATION_MANUAL.md); without it those cards stay empty. You can switch at
any time — just paste the other file's contents into the raw configuration editor, the URLs and the
sidebar entry stay the same.

---

## If it does not work

**"No Modbus TCP connection … refused or immediately closed the session"**

The wallbox serves **only one Modbus TCP client at a time**. This message appears when another
client is already connected. Typical causes:

- a second Home Assistant instance polls the same wallbox
- an old YAML `modbus:` block in `configuration.yaml` holds the connection in parallel to the
  integration — the block is superseded by the integration and can be removed
- an energy manager or charge controller uses the HEMS interface

You can check this from any machine: if the wallbox accepts the TCP connection and closes it
immediately, the slot is taken.

**Sensors read 0 or "unavailable"** — enable Modbus TCP on the device (register `2010` must report
`1` or `2`). After a firmware update the wallbox may report `systemStatus: UpdateInProgress` for
several minutes and reject every Modbus connection during that time; Home Assistant reconnects on
its own afterwards.

**The availability switch does nothing** — register 124 is read-only in protocol version 1.5
according to the manufacturer documentation.

Further cases and the complete register reference are in the
[manual installation](INSTALLATION_MANUAL.md).

---

## Support & license

- **Issues**: [nobelp/mennekes-amtron-ha/issues](https://github.com/nobelp/mennekes-amtron-ha/issues)
- **Home Assistant Community**: [Discourse](https://discourse.home-assistant.io)
- **Change history**: [CHANGELOG.md](CHANGELOG.md)

MIT licence, see [LICENSE](LICENSE). Copyright © 2026 nobelp.
