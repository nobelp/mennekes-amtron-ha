# Changelog

Alle wesentlichen Änderungen an diesem Projekt. Versionierung nach
[Semantic Versioning](https://semver.org/lang/de/).

*All notable changes to this project. Versioning follows
[Semantic Versioning](https://semver.org/).*

---

## [2.2.0] – 2026-08-22

Die Kostenberechnung folgt der Währung von Home Assistant — die Integration ist nicht mehr auf CHF
festgelegt.

*The cost calculation follows the Home Assistant currency — the integration is no longer fixed to
CHF.*

> **Nach dem Update:** Währung unter **Einstellungen → System → Allgemein** prüfen. Home Assistant
> steht ab Werk auf `EUR`; wer in CHF abrechnet, stellt dort `CHF` ein.
>
> *After the update: check the currency under **Settings → System → General**. Home Assistant
> defaults to `EUR`; if you bill in CHF, select `CHF` there.*

### Hinzugefügt / Added

| Deutsch | English |
|---------|---------|
| Die Integration nutzt die Währung von Home Assistant (**Einstellungen → System → Allgemein**), wie das Energie-Dashboard. Eine Änderung dort wirkt sofort, ohne Neustart. Der Strompreis wird in dieser Währung eingegeben. | The integration uses the Home Assistant currency (**Settings → System → General**), like the Energy dashboard. Changing it there takes effect immediately, no restart. The electricity price is entered in that currency. |
| `sensor.mennekes_amtron_total_cost` trägt die Home-Assistant-Währung als Einheit und die Geräteklasse `monetary`. | `sensor.mennekes_amtron_total_cost` carries the Home Assistant currency as its unit and the `monetary` device class. |
| Die Attribute `currency` und `price_per_kwh` an `sensor.mennekes_amtron_sessions_summary` sowie `currency` an `sensor.mennekes_amtron_known_vehicles`; das mitgelieferte Dashboard zeigt die Währung in den Kostenspalten. | The attributes `currency` and `price_per_kwh` on `sensor.mennekes_amtron_sessions_summary` and `currency` on `sensor.mennekes_amtron_known_vehicles`; the shipped dashboard shows the currency in the cost columns. |
| **Manuelle Installation:** Helfer `input_text.wallbox_currency` (Standard `CHF`) und `input_number.wallbox_price_per_kwh` — letzterer wurde in der Doku referenziert, aber nie mitgeliefert. `wallbox_dashboard.yaml` (Vollversion) zeigt die Währung aus dem Helfer; `wallbox_config.json` heisst der Preisschlüssel jetzt `price_per_kwh` (alter Schlüssel `price_per_kwh_chf` wird weiter gelesen). | **Manual installation:** helpers `input_text.wallbox_currency` (default `CHF`) and `input_number.wallbox_price_per_kwh` — the latter was referenced in the docs but never shipped. `wallbox_dashboard.yaml` (full version) shows the currency from the helper; in `wallbox_config.json` the price key is now `price_per_kwh` (legacy key `price_per_kwh_chf` still read). |

### Geändert / Changed

| Deutsch | English |
|---------|---------|
| **Dashboard-Anpassung nötig:** Das Attribut `cost_chf` je Ladevorgang in `sessions` heisst jetzt `cost`. Wer das Dashboard vor 2.2.0 eingefügt hat, ersetzt `s.cost_chf` durch `s.cost` oder fügt die neue Datei erneut ein. | **Dashboard update required:** the per-session attribute `cost_chf` in `sessions` is now `cost`. If you pasted the dashboard before 2.2.0, replace `s.cost_chf` with `s.cost` or paste the new file again. |
| `sensor.mennekes_amtron_total_cost` nutzt die Zustandsklasse `total` statt `total_increasing`, wie Home Assistant es für Geldbeträge verlangt. | `sensor.mennekes_amtron_total_cost` uses the `total` state class instead of `total_increasing`, as Home Assistant requires for monetary values. |
| **Manuelle Installation, Anpassung nötig:** Die Kosten-Template-Sensoren heissen jetzt `sensor.wallbox_kosten_gesamt` und `sensor.wallbox_kosten_aktueller_monat` (vorher mit `_chf`). Template-Sensoren können keine dynamische Einheit, daher tragen sie keine feste Einheit mehr, sondern das Attribut `currency`. `templates/wallbox.yaml`, `input_*_wallbox.yaml` und `wallbox_dashboard.yaml` neu kopieren; die alten `_chf`-Entitäten löschen. Im Fetch-Ergebnis heisst `cost_chf` jetzt `cost`, `total_cost_chf` jetzt `total_cost`. | **Manual installation, update required:** the cost template sensors are now `sensor.wallbox_kosten_gesamt` and `sensor.wallbox_kosten_aktueller_monat` (previously with `_chf`). Template sensors cannot have a dynamic unit, so they no longer carry a fixed unit but the attribute `currency`. Re-copy `templates/wallbox.yaml`, `input_*_wallbox.yaml` and `wallbox_dashboard.yaml`; delete the old `_chf` entities. In the fetch output `cost_chf` is now `cost`, `total_cost_chf` is now `total_cost`. |

### Behoben / Fixed

| Deutsch | English |
|---------|---------|
| Änderungen an Strompreis und Intervall unter **Konfigurieren** wurden gespeichert, aber nie angewendet — die Integration las weiterhin die Werte aus der Ersteinrichtung. Optionen haben jetzt Vorrang. | Changes to the electricity price and interval under **Configure** were stored but never applied — the integration kept reading the values from the initial setup. Options now take precedence. |
| Die Feldbezeichnungen im Einrichtungsdialog passten nicht zu den Feldschlüsseln (`electricity_price` statt `price_per_kwh`, `password` statt `api_password`), daher erschienen die technischen Namen. Ebenso die Fehlermeldungen. | The field labels in the setup dialog did not match the field keys (`electricity_price` instead of `price_per_kwh`, `password` instead of `api_password`), so the technical names were shown. Same for the error messages. |

---

## [2.1.1] – 2026-08-02

Die Integration erfüllt nun auch die hassfest-Prüfung für die Aufnahme in den
offiziellen HACS-Katalog. Das Laufzeitverhalten der Integration ist unverändert.

*The integration now also passes hassfest validation for inclusion in the
official HACS catalogue. Runtime behaviour is unchanged.*

### Geändert / Changed

| Deutsch | English |
|---------|---------|
| Offiziellen hassfest-Workflow ergänzt und Versionsnummer für den Katalog-Release auf 2.1.1 erhöht. | Added the official hassfest workflow and bumped the version to 2.1.1 for the catalogue release. |

---

## [2.1.0] – 2026-07-31

Systemereignisse und RFID-Zuordnung laufen jetzt ohne manuelle Installation.

*System events and RFID assignment now work without the manual installation.*

### Hinzugefügt / Added

| Deutsch | English |
|---------|---------|
| Die Integration liest das Ereignisprotokoll selbst über `GET /api/v1/SystemEvents`. Der Sensor `sensor.mennekes_amtron_system_events` liefert die Gesamtzahl als Zustand und die Einträge als Attribut. Command-Line-Sensoren, `shell_command` und die Python-Scripts sind dafür nicht mehr nötig. | The integration reads the event log itself via `GET /api/v1/SystemEvents`. The `sensor.mennekes_amtron_system_events` sensor exposes the total as its state and the entries as an attribute. Command-line sensors, `shell_command` and the Python scripts are no longer needed for this. |
| Filter für die Ereignisliste als Entitäten: `select.mennekes_amtron_event_level_filter`, `select.mennekes_amtron_event_id_filter` und `text.mennekes_amtron_event_search`. Die fünf YAML-Helfer entfallen. | Filters for the event list as entities: `select.mennekes_amtron_event_level_filter`, `select.mennekes_amtron_event_id_filter` and `text.mennekes_amtron_event_search`. The five YAML helpers are gone. |
| RFID-Zuordnung in der Integration: `select.mennekes_amtron_rfid` füllt sich automatisch aus der Ladehistorie, `text.mennekes_amtron_vehicle_name` nimmt den Namen auf, `button.mennekes_amtron_assign_vehicle` speichert die Zuordnung. | RFID assignment inside the integration: `select.mennekes_amtron_rfid` fills itself from the charging history, `text.mennekes_amtron_vehicle_name` takes the name, `button.mennekes_amtron_assign_vehicle` stores the mapping. |
| Die Zuordnung liegt in den Optionen des Konfigurationseintrags — kein `wallbox_vehicles.json`, keine Scripts. `sensor.mennekes_amtron_known_vehicles` zeigt sie samt Verbrauch je Fahrzeug. | The mapping lives in the config entry options — no `wallbox_vehicles.json`, no scripts. `sensor.mennekes_amtron_known_vehicles` shows it together with the consumption per vehicle. |
| Buttons zum Abrufen: `button.mennekes_amtron_refresh_charging_history` und `button.mennekes_amtron_refresh_system_events`. | Refresh buttons: `button.mennekes_amtron_refresh_charging_history` and `button.mennekes_amtron_refresh_system_events`. |

### Geändert / Changed

| Deutsch | English |
|---------|---------|
| Ladehistorie und Systemereignisse werden **nur auf Knopfdruck** abgerufen, dazu einmal beim Start. Vorher lief die Historie stündlich. Jeder REST-Aufruf kostet einen vollständigen Nonce- und Login-Vorgang, deshalb bringt ein Timer nichts. | Charging history and system events are fetched **on button press only**, plus once at startup. The history previously ran hourly. Every REST call costs a full nonce and login round trip, so a timer buys nothing. |
| Der Reiter Systemereignisse des mitgelieferten Dashboards zeigt die echte Ereignisliste mit Filterleiste statt eines Hinweistexts; der Konfigurations-Reiter enthält die RFID-Verwaltung. | The system events tab of the shipped dashboard shows the real event list with a filter bar instead of a placeholder note; the configuration tab contains the RFID management. |
| Der Session-Coordinator nutzt den konfigurierten API-Port; er war fest auf Port 80 verdrahtet. | The session coordinator uses the configured API port; it was hardcoded to port 80. |
| Eine Fahrzeugzuordnung lädt den Eintrag nicht mehr neu, sondern beschriftet die zwischengespeicherte Historie neu — ein Reload würde die einzige Modbus-Verbindung der Wallbox kappen. | Assigning a vehicle no longer reloads the entry but re-labels the cached history — a reload would drop the wallbox's single Modbus connection. |
| Der Options-Dialog überschreibt die Fahrzeugzuordnung nicht mehr. | The options dialog no longer overwrites the vehicle mapping. |

### Behoben / Fixed

| Deutsch | English |
|---------|---------|
| Der Pfad für die Systemereignisse war falsch: `SystemManagement/SystemEvents` liefert HTTP 404, richtig ist `SystemEvents`. Ohne `take=` gibt die Wallbox nur 100 Einträge zurück. | The system events path was wrong: `SystemManagement/SystemEvents` returns HTTP 404, the correct one is `SystemEvents`. Without `take=` the wallbox only returns 100 entries. |
| Der Level eines Ereignisses kommt aus `parsedSeverity`; das Feld `severity` meldet auf Firmware 1.5 bei jedem Eintrag `Error` und ist unbrauchbar. | The level of an event comes from `parsedSeverity`; the `severity` field reports `Error` for every entry on firmware 1.5 and is unusable. |

---

## [2.0.0] – 2026-07-31

Erste konsolidierte Version. Frühere Releases sind zurückgezogen.

*First consolidated release. Earlier releases have been withdrawn.*

### Behoben / Fixed

| Deutsch | English |
|---------|---------|
| Zählerregister werden als 32-Bit-Werte über beide Register dekodiert, High-Word zuerst. Leistung, Gesamtleistung und Spannung wurden zuvor nur aus dem High-Word gelesen und meldeten konstant `0`. | Meter registers are decoded as 32-bit values across both registers, high word first. Power, total power and voltage were previously read from the high word only and reported a constant `0`. |
| Energie, Strom und Session-Werte hatten die Wortreihenfolge vertauscht — ein Zählerstand von 990,32 kWh erschien als 477 102,095 kWh. | Energy, current and session values had their word order swapped — a meter reading of 990.32 kWh appeared as 477,102.095 kWh. |
| Registeradressen für L2 und L3 korrigiert: ein `int32` belegt zwei Register, aufeinanderfolgende Phasen liegen 2 auseinander, nicht 1. | Corrected the L2 and L3 register addresses: an `int32` spans two registers, so consecutive phases are 2 apart, not 1. |
| Fehlercodes werden als dokumentierte 4 × `uint32` aus den Registern 105–112 gelesen statt als 4 × `uint16`. | Error codes are read as the documented 4 × `uint32` from registers 105–112 instead of 4 × `uint16`. |
| Weist die Wallbox die Modbus-Sitzung ab, erscheint eine verwertbare Meldung statt eines rohen `pymodbus`-Tracebacks. | If the wallbox refuses the Modbus session, a usable message appears instead of a bare `pymodbus` traceback. |
| Der Konfigurationsdialog meldet falsche Zugangsdaten korrekt; bei HTTP 401/403 erschien vorher ein unbekannter Fehler. | The configuration dialog reports invalid credentials correctly; HTTP 401/403 previously surfaced as an unknown error. |
| Der konfigurierte API-Port wird verwendet statt fest Port 80. | The configured API port is used instead of a hardcoded port 80. |
| Blocklesungen prüfen die Registeranzahl, statt Teilergebnisse still auf `0` zu setzen. | Block reads verify the register count instead of silently zeroing partial results. |

### Hinzugefügt / Added

| Deutsch | English |
|---------|---------|
| Zwei Dashboards mit je vier Reitern werden mit der Integration ausgeliefert. `wallbox_dashboard_integration.yaml` nutzt ausschließlich Entitäten der Integration, `wallbox_dashboard.yaml` ist die Vollversion für Installationen mit YAML-Teil. | Two dashboards with four tabs each ship with the integration. `wallbox_dashboard_integration.yaml` uses only entities the integration creates; `wallbox_dashboard.yaml` is the full version for installations with the YAML part. |
| Deutsche Übersetzung des Konfigurationsdialogs samt Feldbeschreibungen. | German translation of the configuration dialog including field descriptions. |
| Dokumentierte Unterstützung für **AMTRON 4You 400/500** und **4Business 600/700** — alle nutzen denselben Modbus-TCP-Registersatz. | Documented support for **AMTRON 4You 400/500** and **4Business 600/700** — all share the same Modbus TCP register set. |
| Vollständige Modbus-Registerreferenz nach Protokollversion 1.5, inklusive Hinweis auf die nur lesbaren Register. | Complete Modbus register reference based on protocol version 1.5, including a note on the read-only registers. |
| Schritt-für-Schritt-Anleitung zum Anlegen des Dashboards in der Seitenleiste. | Step-by-step guide for adding the dashboard to the sidebar. |

### Geändert / Changed

| Deutsch | English |
|---------|---------|
| Dokumentation aufgeteilt in Schnellstart (`README.md`, `README.en.md`) und manuelle Installation (`INSTALLATION_MANUELL.md`, `INSTALLATION_MANUAL.md`), jeweils deutsch und englisch. | Documentation split into quick start (`README.md`, `README.en.md`) and manual installation (`INSTALLATION_MANUELL.md`, `INSTALLATION_MANUAL.md`), each in German and English. |
| Repository aufgeräumt: Entwicklungshilfen und interne Arbeitsnotizen werden nicht mehr veröffentlicht. | Repository cleaned up: development helpers and internal working notes are no longer published. |
| Versionierung auf **2.0.0** konsolidiert; der Integrationsname verliert den Zusatz `TEST`. | Versioning consolidated to **2.0.0**; the integration name loses its `TEST` suffix. |
| Alle Repository-Links zeigen auf `nobelp/mennekes-amtron-ha`. | All repository links point at `nobelp/mennekes-amtron-ha`. |

### Hinweis / Note

| Deutsch | English |
|---------|---------|
| Die Wallbox bedient **nur einen Modbus-TCP-Client gleichzeitig**. Eine zweite Home-Assistant-Instanz, ein paralleler YAML-`modbus:`-Block oder ein externer Energiemanager verhindern die Verbindung. | The wallbox serves **only one Modbus TCP client at a time**. A second Home Assistant instance, a parallel YAML `modbus:` block or an external energy manager will block the connection. |
| Register 124 (Verfügbarkeit) ist in Protokollversion 1.5 laut Herstellerdokumentation nur lesbar — der zugehörige Schalter kann nicht schreiben. | Register 124 (availability) is read-only in protocol version 1.5 according to the manufacturer documentation — the corresponding switch cannot write to it. |
