# Mennekes AMTRON Wallbox – Home Assistant Integration

**Deutsch (Schnellstart)** · [Manuelle Installation](INSTALLATION_MANUELL.md) · [English (quick start)](README.en.md) · [Manual installation (English)](INSTALLATION_MANUAL.md)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Release](https://img.shields.io/github/v/release/nobelp/mennekes-amtron-ha)](https://github.com/nobelp/mennekes-amtron-ha/releases)

Bindet eine Mennekes AMTRON Wallbox in Home Assistant ein — Einrichtung vollständig über die
Weboberfläche, ohne YAML-Dateien:

- **Echtzeit-Monitoring** via Modbus TCP: Ladestatus, Spannung, Strom, Leistung, Energie
- **Ladehistorie** via REST API: Sessions, Fahrzeugzuordnung, Kosten
- **Steuerung**: HEMS-Limit, Safe Current, Ladepause, Verfügbarkeit
- **Dashboard** mit vier Reitern, wird mitgeliefert

> Diese Seite beschreibt den **automatisierten Weg**: HACS, Konfigurationsdialog, Dashboard
> einfügen — fertig. Wer zusätzlich Template-Sensoren, Fahrzeugzuordnung per RFID und
> Systemereignis-Auswertung möchte, folgt der [manuellen Installation](INSTALLATION_MANUELL.md).

---

## Unterstützte Modelle

**AMTRON 4You 400/500** und **AMTRON 4Business 600/700** kommunizieren identisch — gleicher
Modbus-TCP-Registersatz auf Port 502, Unit-ID 1. Die Integration deckt dieses gesamte Portfolio ab,
einschließlich Untervarianten wie 4Business 730 oder 4You 550. Getestet auf einer
**AMTRON 4Business 730 11 C2** mit Firmware 1.5.41.

Voraussetzung am Gerät: Protokollversion **1.5** und aktiviertes Modbus TCP. Register `2010` meldet
den Modus — `0` = aus, `1` = nur lesen, `2` = lesen und schreiben. Für HEMS-Limit und Safe Current
ist `2` erforderlich.

---

## Schritt 1: Integration installieren

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=nobelp&repository=mennekes-amtron-ha&category=integration)

1. Auf den HACS-Button oben klicken, oder in HACS über **⋮ → Benutzerdefinierte Repositories**
   `https://github.com/nobelp/mennekes-amtron-ha` als Kategorie **Integration** hinzufügen
2. **„Mennekes AMTRON"** suchen und **herunterladen**
3. Home Assistant **neu starten**

---

## Schritt 2: Wallbox konfigurieren

**Einstellungen → Geräte & Dienste → Integration hinzufügen → „Mennekes AMTRON"**

![Konfigurationsdialog der Mennekes AMTRON Integration mit den Feldern IP-Adresse, API-Port, Installer-Passwort, Modbus-Port, Strompreis und Aktualisierungsintervall](docs/images/config-flow-ui.png)

| Feld | Bedeutung | Standard |
|------|-----------|----------|
| **IP-Adresse oder Hostname** | Adresse der Wallbox im Netzwerk, z. B. `192.168.2.179` oder `wallbox.local` | – (Pflicht) |
| **API-Port** | HTTP-Port für die REST-Aufrufe | `80` |
| **Installer-Passwort** | Passwort des Installer-Zugangs der Wallbox | – (Pflicht) |
| **Modbus-Port** | TCP-Port des Modbus-Protokolls | `502` |
| **Strompreis (CHF/kWh)** | Grundlage der Kostenberechnung | `0.29` |
| **Aktualisierungsintervall** | Abstand der Sensor-Updates in Sekunden (1–3600) | `30` |

Nach **OK** legt die Integration ein Gerät mit rund 35 Entitäten an. Modell, Firmware-Version und
Seriennummer liest sie selbst von der Wallbox — das Modell muss nicht ausgewählt werden.

Strompreis und Intervall lassen sich später jederzeit über **Konfigurieren** am Integrationseintrag
ändern.

---

## Schritt 3: Dashboard einrichten

Die Dashboard-Definition wird mitgeliefert und liegt nach der Installation unter
`/config/custom_components/mennekes_amtron/dashboards/`.

**3.1 Dashboard anlegen** — **Einstellungen → Dashboards → „+ Dashboard hinzufügen" →
„Neues Dashboard von Grund auf"**:

| Feld | Wert |
|---|---|
| **Titel** | `Wallbox` |
| **Symbol** | `mdi:ev-station` |
| **URL** | `dashboard-wallbox` |
| **In Seitenleiste anzeigen** | aktiviert |

> Die URL **muss einen Bindestrich enthalten** — Home Assistant lehnt `wallbox` und
> `dashboard_wallbox` mit *„Url path needs to contain a hyphen (-)"* ab.

**3.2 Inhalt einfügen** — das neue Dashboard öffnen, oben rechts **Stift → ⋮ →
„Rohkonfigurationseditor"**, den vorhandenen Text vollständig durch den Inhalt dieser Datei
ersetzen und speichern:

```
/config/custom_components/mennekes_amtron/dashboards/wallbox_dashboard_integration.yaml
```

Diese Variante referenziert ausschließlich Entitäten, die die Integration selbst anlegt — es
erscheinen keine Karten mit „Entität nicht gefunden". Ein Neustart ist nicht nötig.

**Ergebnis:** vier Reiter.

| Reiter | URL | Inhalt |
|---|---|---|
| Übersicht | `/dashboard-wallbox/wallbox-main` | Status, aktuelle bzw. letzte Ladesession, Energie, Leistung, Spannung & Strom, gelesene Limits |
| History | `/dashboard-wallbox/wallbox-history` | Summen, Monatstabelle, Verbrauch je Fahrzeug, letzte Ladevorgänge |
| Systemereignisse | `/dashboard-wallbox/wallbox-systemlogs` | Hinweis zur optionalen Ereignisauswertung |
| Konfiguration | `/dashboard-wallbox/wallbox-config` | HEMS-Limit, Safe Current, Timeout, Ladepause, Verfügbarkeit |

Die zweite mitgelieferte Datei `wallbox_dashboard.yaml` ist die **Vollversion** mit
Systemereignis-Filter, DLM-Karten und Fahrzeugzuordnung. Sie setzt die
[manuelle Installation](INSTALLATION_MANUELL.md) voraus; ohne diese bleiben ihre Karten leer. Ein
Wechsel ist jederzeit möglich — einfach den Inhalt der anderen Datei im Rohkonfigurationseditor
einsetzen, URLs und Seitenleisteneintrag bleiben unverändert.

---

## Wenn es nicht funktioniert

**„No Modbus TCP connection … refused or immediately closed the session"**

Die Wallbox bedient **nur einen Modbus-TCP-Client gleichzeitig**. Diese Meldung erscheint, wenn
bereits ein anderer Client verbunden ist. Typische Fälle:

- eine zweite Home-Assistant-Instanz fragt dieselbe Wallbox ab
- ein alter YAML-`modbus:`-Block in der `configuration.yaml` belegt die Verbindung parallel zur
  Integration — der Block ist durch die Integration ersetzt und kann entfernt werden
- ein Energiemanager oder Ladecontroller nutzt die HEMS-Schnittstelle

Prüfen lässt sich das von einem beliebigen Rechner aus: nimmt die Wallbox die TCP-Verbindung an und
trennt sie sofort wieder, ist der Slot belegt.

**Sensoren zeigen 0 oder „unavailable"** — Modbus TCP am Gerät aktivieren (Register `2010`
muss `1` oder `2` melden). Nach einem Firmware-Update kann die Wallbox mehrere Minuten
`systemStatus: UpdateInProgress` melden und in dieser Zeit alle Modbus-Verbindungen abweisen; Home
Assistant verbindet sich danach selbstständig.

**Der Verfügbarkeits-Schalter reagiert nicht** — Register 124 ist in Protokollversion 1.5 laut
Herstellerdokumentation nur lesbar.

Weitere Fälle und die vollständige Registerreferenz stehen in der
[manuellen Installation](INSTALLATION_MANUELL.md).

---

## Support & Lizenz

- **Issues**: [nobelp/mennekes-amtron-ha/issues](https://github.com/nobelp/mennekes-amtron-ha/issues)
- **Home Assistant Community**: [Discourse](https://discourse.home-assistant.io)
- **Änderungshistorie**: [CHANGELOG.md](CHANGELOG.md)

MIT-Lizenz, siehe [LICENSE](LICENSE). Copyright © 2026 nobelp.
