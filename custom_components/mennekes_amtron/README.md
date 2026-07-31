# Mennekes AMTRON 4Business 730 11 C2 - Home Assistant Integration

Vollständige Integration einer Mennekes Wallbox (Firmware 1.5.41) in Home Assistant über Modbus TCP mit Fallback-Netzwerk.

## Hardware-Konfiguration

- **Wallbox Model**: Mennekes AMTRON 4Business 730 11 C2
- **Firmware**: 1.5.41
- **Primäre Verbindung**: 192.168.2.179:502 (Slave ID 1) ✓ getestet
- **Fallback-Verbindung**: 10.84.19.55:502 (Slave ID 1) - Mobilfunk-Backup

## Installation & Konfiguration

### 1. Configuration.yaml vorbereiten

Füge folgende !include Statements in deine `configuration.yaml` ein:

```yaml
# Wallbox Modbus Integration
modbus: !include modbus_wallbox.yaml

# Wallbox Helper Entities
input_number: !include input_wallbox.yaml
input_boolean: !include input_wallbox.yaml

# Wallbox Template Sensoren
template: !include template_sensors_wallbox.yaml

# Wallbox Automationen
automation: !include automations_wallbox.yaml
```

### 2. Dateistruktur

```
config/
├── configuration.yaml
├── modbus_wallbox.yaml                 # Modbus Konfiguration (alle Register)
├── input_wallbox.yaml                  # Helper Entities (Slider, Schalter)
├── template_sensors_wallbox.yaml       # Template Sensoren (Umrechnung, Dekodierung)
├── automations_wallbox.yaml            # Automationen (Schreiben, Benachrichtigungen)
└── README_wallbox.md                   # Diese Datei
```

### 3. Home Assistant neustarten

Nach dem Hinzufügen der Include-Statements Home Assistant neu starten, damit die neue Modbus-Integration geladen wird.

## Funktionalität

### Verfügbare Sensoren

#### System-Information
- **Firmware Version**: v1.5.41 (ASCII)
- **Protokoll Version**: Modbus TCP Spezifikation v1.07
- **Chargepoint Model**: Zusammengesetzter Model-String aus 5x 32-bit Register
- **Modbus Address Offset**: Konfigurierbar

#### Ladestatus
- **CP Status**: Verfügbar, Besetzt, Reserviert, Nicht verfügbar, Fehler, Vorbereitung, **Lädt**, Pause, Abgeschlossen
- **Vehicle State**: Zustand A-E (Kein Fahrzeug, Angesteckt, Laden, Mit Lüftung, Fehler)
- **Charging Status**: Automatische deutsche Statusbeschreibung
- **Plug Lock Status**: Gesperrt/Entsperrt

#### Energiemesswerte
- **Spannung**: L1, L2, L3 (V) - **getestet: 230V, 232V, 233V ✓**
- **Strom**: L1, L2, L3 (mA → A konvertiert)
- **Leistung**: L1, L2, L3, Gesamt (W)
- **Energie**: L1, L2, L3, Gesamt (Wh → kWh konvertiert) - **getestet: 342.972 Wh ✓**

#### Ladesession
- **Geladene Energie**: Session (Wh → kWh)
- **Ladedauer**: formatiert als hh:mm:ss
- **Ladestrom**: aktueller Strom (A)
- **Max Strom EV**: Maximaler Fahrzeugstrom (A)
- **Start/End Time**: BCD-formatierte Zeit

#### Fehlerbehandlung
- **Error Codes**: Dekodiert als lesbare Textliste:
  - RCM ausgelöst
  - Fahrzeugzustand E
  - Mode3 Dioden-Check
  - MCB Type2/Schuko ausgelöst
  - RCD ausgelöst
  - Kontakt verschweißt
  - Backend getrennt
  - Aktuator-Fehler
  - Firmware-Update läuft
  - Tilt-Fehler
  - Falsches CP/PR-Kabel
  - Type2 Überlast
  - Keine Stromversorgung

#### Dynamic Load Management (DLM)
- **DLM Mode**: Disabled, Master+Slave, Master, Slave AutoDiscovery, Slave Fixed-IP
- **DLM Limits**: Sub-Distribution Limits pro Phase (L1-L3)
- **DLM Status**: Anzahl verbundener Slaves, verfügbare Ströme

### Steuerung (Schreib-Register)

#### HEMS Stromlimit (Register 1000)
- **Bereich**: 0-16 A
- **0**: Laden pausiert
- **6-16**: Aktiver Ladestrom
- **Steuerung**: `input_number.wallbox_hems_current_limit` Slider
- **Automation**: Änderungen werden automatisch auf die Wallbox geschrieben

#### CP Availability (Register 124)
- **Werte**: 0 = unavailable, 1 = available
- **Steuerung**: `input_boolean.wallbox_cp_availability` Toggle
- **Automation**: Änderungen werden automatisch geschrieben

#### Safe Current (Register 131)
- **Bereich**: 0-32 A
- **Steuerung**: `input_number.wallbox_safe_current` Slider
- **Automation**: Wird beim Ändern geschrieben

#### Comm Timeout (Register 132)
- **Bereich**: 1-300 s
- **Steuerung**: `input_number.wallbox_comm_timeout` Slider
- **Automation**: Wird beim Ändern geschrieben

## Fallback-Logik

Die Wallbox ist über zwei Netzwerkpfade erreichbar:

1. **Primär**: 192.168.2.179:502 (Standard-Ethernet)
2. **Fallback**: 10.84.19.55:502 (Mobilfunk-Backup)

Die Modbus TCP Konfiguration nutzt einen einzigen Host mit der primären IP. Falls diese nicht erreichbar ist:

**Manueller Fallback**: Bearbeite `modbus_wallbox.yaml` und ändere die `host` von `192.168.2.179` zu `10.84.19.55`.

**Automatischer Fallback (Optional)**: Implementierbar durch:
- HA-native Fallover-Mechanismen (erfordert zusätzliche Automation)
- oder separaten Modbus-Hub mit automatischer IP-Auswahl

Für stabilen Produktionseinsatz wird empfohlen, die primäre Ethernet-Verbindung zu nutzen.

## Automationen & Benachrichtigungen

### Automat. Stromlimit-Steuerung
- Änderungen am HEMS-Slider (`input_number.wallbox_hems_current_limit`) werden sofort auf Register 1000 geschrieben
- Ermöglicht dynamische Lastverteilung und Energiemanagement

### Fehlerbenachrichtigungen
- Alert bei Fehler-Erkennungen (RCM, RCD, Backend, etc.)
- Titel: "🚨 Wallbox Fehler"
- Nachricht mit konkreter Fehlerliste

### Ladevorgänge
- **Ladestart**: Benachrichtigung mit aktuellem Strom und Spannung
- **Ladeende**: Benachrichtigung mit geladener Energie und Ladedauer
- **Fahrzeug angesteckt**: Warnung beim Anstecken

### Status-Überwachung
- **Nicht erreichbar**: Warnung nach 30 Sekunden Ausfall
- **Hohe Strombelastung**: Alert bei > 10kW über 5 Minuten
- **CP Status Änderung**: Logging von wichtigen Zustandsübergängen

## Dashboard-Integration

### Energie-Dashboard
Die folgenden Sensoren sind für das Home Assistant Energie-Dashboard optimiert:

- `sensor.wallbox_total_energy_kwh` (device_class: energy, state_class: total_increasing)
- `sensor.wallbox_energy_l1_kwh` (per Phase)
- `sensor.wallbox_energy_l2_kwh`
- `sensor.wallbox_energy_l3_kwh`

### Custom Card Beispiel (für Lovelace)

```yaml
type: custom:mushroom-template-card
primary: "{{ states('sensor.wallbox_charging_status') }}"
secondary: "{{ states('sensor.wallbox_session_energy_kwh') }} kWh"
icon: mdi:ev-station
icon_color: |
  {% if states('sensor.wallbox_charging_status') == 'Lädt' %}
    amber
  {% elif states('sensor.wallbox_charging_status') == 'Fehler' %}
    red
  {% else %}
    green
  {% endif %}
```

## Modbus Register Referenz

### Lesende Register (Read-Only)

| Register | Größe | Typ | Einheit | Beschreibung |
|----------|-------|-----|--------|--------------|
| 100-101 | uint32 | ASCII | - | Firmware Version |
| 104 | uint16 | enum | - | OCPP CP Status |
| 105-112 | 4x uint32 | Bitmask | - | Error Codes 1-4 |
| 120-121 | uint32 | ASCII | - | Protocol Version |
| 122 | uint16 | enum | - | Vehicle State |
| 142-151 | 5x uint32 | ASCII | - | Chargepoint Model |
| 200-227 | uint32 | - | V, A, W, Wh | Meter Values (Spannung, Strom, Leistung, Energie) |
| 600-635 | uint16 | - | A | DLM Configuration & Status |
| 705-730 | - | - | Wh, A, s | Charge Process Data |

### Schreib-Register (Read/Write)

| Register | Größe | Typ | Bereich | Beschreibung |
|----------|-------|-----|---------|--------------|
| 124 | uint16 | enum | 0-1 | CP Availability |
| 131 | uint16 | uint | A | Safe Current |
| 132 | uint16 | uint | s | Comm Timeout |
| 613-615 | uint16 | uint | A | DLM Operator Limits |
| 1000 | uint16 | uint | 0-16 | HEMS Current Limit |

## Troubleshooting

### Wallbox nicht erreichbar

1. **Primäre IP prüfen**:
   ```bash
   ping 192.168.2.179
   ```

2. **Fallback IP prüfen**:
   ```bash
   ping 10.84.19.55
   ```

3. **Modbus Port prüfen**:
   ```bash
   nc -zv 192.168.2.179 502
   ```

4. **Home Assistant Logs prüfen**:
   - Developer Tools → Logs
   - Filtern nach "modbus"

### Sensoren zeigen "unavailable"

- Wallbox ist nicht erreichbar (siehe oben)
- Falsche Slave ID (aktuell: 1)
- Kommunikations-Timeout zu kurz eingestellt

### Register-Schreiben funktioniert nicht

1. **Automatische Modbus-Automation deaktivieren** (während Debugging)
2. **Manual Write in Developer Tools testen**:
   ```yaml
   service: modbus.write_register
   data:
     hub: "Mennekes AMTRON Wallbox"
     slave: 1
     address: 1000
     value: 10
   ```

## Performance-Tipps

- **Modbus Scan Interval**: Standardmäßig 30 Sekunden (in modbus_wallbox.yaml anpassbar)
- **Template Sensor Refresh**: Automatisch bei Quell-Sensor-Update
- **Automation Debouncing**: Mode "single" verhindert mehrfaches Triggern

## Sicherheit

- **Authentifizierung**: Modbus TCP hat keine eingebaute Authentifizierung
  - Nutz Netzwerk-Isolation oder VPN für Produktivumgebungen
- **Schreibvorgänge**: Nur über explizite Automationen möglich
  - input_number/input_boolean dienen als Stellschrauben
- **IP Whitelisting**: Empfohlen auf Firewall-Ebene

## Version & Updates

- **Home Assistant Version**: 2024.1+
- **Wallbox Firmware**: 1.5.41
- **Modbus Spec**: ECU-BRx Modbus TCP Server v1.07
- **Letztes Update**: 2026-06-02

## Support

Bei Fragen oder Problemen:
1. Home Assistant Logs prüfen (Settings → System → Logs)
2. Wallbox Bedienungsanleitung (Modbus Register)
3. Home Assistant Community Forum

---

**Getestete Funktionalität**:
- ✓ Modbus TCP Verbindung 192.168.2.179:502
- ✓ Spannungsmessung L1-L3 (230V, 232V, 233V)
- ✓ Energiemessung Gesamt (342.972 Wh)
- ✓ CP Status Abfrage
- ✓ Vehicle State Detection
- ✓ Error Code Dekodierung
