#!/usr/bin/env python3
"""
Weist einem RFID einen Fahrzeugnamen zu.
Liest: RFID_OPTION (Format: "A1B2C3D4E5F6 — Kessi"), NAME (neuer Name)
Schreibt: /config/wallbox_vehicles.json (bestehende Einträge bleiben erhalten)
"""
import os
import json

OUTPUT_FILE = "/config/wallbox_vehicles.json"

rfid_option = os.environ.get("RFID_OPTION", "").strip()
name = os.environ.get("VEHICLE_NAME", "").strip()

# Parse RFID from option string like "A1B2C3D4E5F6 — Kessi"
rfid = rfid_option.split(" — ")[0].strip().split(" ")[0].strip()

if not rfid or not name:
    print(f"Fehler: RFID='{rfid}' NAME='{name}' — beide Felder erforderlich")
    exit(1)

try:
    with open(OUTPUT_FILE) as f:
        mapping = json.load(f)
except Exception:
    mapping = {}

mapping[rfid] = name

with open(OUTPUT_FILE, "w") as f:
    json.dump(mapping, f, indent=2, ensure_ascii=False)

print(f"OK: {rfid} → {name}")
print(f"Gesamt {len(mapping)} Fahrzeug(e):")
for r, n in mapping.items():
    print(f"  {r} → {n}")
