#!/usr/bin/env python3
"""
Mennekes AMTRON - Ladevorgänge via REST API holen.
Speichert JSON nach /config/wallbox_sessions.json.

Passwort via Umgebungsvariable WALLBOX_PASS oder sys.argv[1].
Fahrzeug-Mapping aus /config/wallbox_vehicles.json (optional).
Strompreis aus /config/wallbox_config.json (optional, default 0.29):
    {"price_per_kwh": 0.29}
Der alte Schlüssel "price_per_kwh_chf" wird weiterhin gelesen. Die Währung ist
nur ein Anzeige-Label und kommt aus input_text.wallbox_currency in Home Assistant.
"""

import sys
import os
import json
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from collections import defaultdict

BASE_URL = os.environ.get("WALLBOX_URL") or "http://192.x.x.x/api/v1"  # Replace 192.x.x.x with your Wallbox IP
OUTPUT_FILE = "/config/wallbox_sessions.json"
VEHICLES_FILE = "/config/wallbox_vehicles.json"
CONFIG_FILE = "/config/wallbox_config.json"

MONTH_NAMES = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Dezember"
}


def get_nonce():
    with urllib.request.urlopen(f"{BASE_URL}/Nonce?nocache={time.time()}", timeout=30) as r:
        return r.read().decode().strip()


def login(password):
    nonce = get_nonce()
    payload = json.dumps({"username": "Installer", "password": password}).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/AuthManagement/login",
        data=payload,
        headers={"Content-Type": "application/json", "X-Nonce": nonce},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read().decode())
        return data.get("token") or data.get("accessToken") or data.get("access_token")


def get_sessions(token, skip=0, take=100):
    nonce = get_nonce()
    to_date = datetime.now(timezone.utc).strftime("%Y-%m-%dT23:59:59.999Z")
    params = urllib.parse.urlencode({
        "skip": skip,
        "take": take,
        "from": "2024-01-01T00:00:00.000Z",
        "to": to_date,
    })
    url = f"{BASE_URL}/ChargingTransactionHistory/ReadFromTo?{params}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"Bearer {token}",
        "X-Nonce": nonce,
        "Cache-Control": "no-cache",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def load_vehicles():
    try:
        with open(VEHICLES_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def load_config():
    try:
        with open(CONFIG_FILE) as f:
            return json.load(f)
    except Exception:
        return {}


def month_label(iso_date):
    if not iso_date or len(iso_date) < 7:
        return "Unbekannt"
    year, month = int(iso_date[:4]), int(iso_date[5:7])
    return f"{MONTH_NAMES.get(month, str(month))} {year}"


def main():
    password = os.environ.get("WALLBOX_PASS") or (sys.argv[1] if len(sys.argv) > 1 else "")
    if not password:
        result = {"error": "No password", "sessions": [], "count": 0, "total_kwh": 0}
        print(json.dumps(result))
        sys.exit(1)

    try:
        vehicles = load_vehicles()
        config = load_config()
        price_per_kwh = float(
            config.get("price_per_kwh", config.get("price_per_kwh_chf", 0.29))
        )

        token = login(password)
        if not token:
            result = {"error": "Login failed", "sessions": [], "count": 0, "total_kwh": 0}
            print(json.dumps(result))
            sys.exit(1)

        data = get_sessions(token)
        items = data if isinstance(data, list) else data.get("list", data.get("items", data.get("data", [])))

        sessions = []
        for s in items:
            end_ts = s.get("stopTimestamp") or s.get("endTimestamp") or s.get("end")
            if not end_ts or str(end_ts).startswith("0001"):
                # Session still active — API returns "0001-01-01T00:00:00Z" as sentinel
                continue
            user_token = s.get("userToken", {})
            rfid = user_token.get("identifier") if isinstance(user_token, dict) else s.get("rfid", "")
            vehicle = vehicles.get(rfid, s.get("whitelistEntryFirstName") or rfid or "Unbekannt")
            energy_kwh = round(s.get("chargedEnergy", 0), 3)
            sessions.append({
                "id": s.get("ocppTransactionId") or s.get("id"),
                "start": s.get("startTimestamp") or s.get("start"),
                "end": end_ts,
                "duration": s.get("chargedTime") or s.get("formattedChargedTime"),
                "energy_kwh": energy_kwh,
                "cost": round(energy_kwh * price_per_kwh, 2),
                "start_meter_kwh": round(s.get("startMeterValue") or s.get("startMeter") or 0, 3),
                "end_meter_kwh": round(s.get("stopMeterValue") or s.get("endMeter") or 0, 3),
                "vehicle": vehicle,
                "rfid": rfid,
                "stop_reason": s.get("stopReason", ""),
            })

        sessions.sort(key=lambda x: x.get("start") or "", reverse=True)

        monthly = defaultdict(lambda: defaultdict(float))
        vehicle_totals = defaultdict(float)
        all_vehicles = set()

        for s in sessions:
            start = s.get("start") or ""
            month_key = start[:7] if len(start) >= 7 else "Unbekannt"
            v = s["vehicle"]
            kwh = s["energy_kwh"]
            monthly[month_key][v] += kwh
            vehicle_totals[v] += kwh
            all_vehicles.add(v)

        vehicles_sorted = sorted(all_vehicles)
        monthly_summary = []
        for month_key in sorted(monthly.keys(), reverse=True):
            total_kwh_month = round(sum(monthly[month_key].values()), 3)
            row = {
                "month": month_key,
                "month_label": month_label(month_key),
                "by_vehicle": {v: round(monthly[month_key].get(v, 0), 3) for v in vehicles_sorted},
                "total": total_kwh_month,
                "cost": round(total_kwh_month * price_per_kwh, 2),
            }
            monthly_summary.append(row)

        total_kwh = round(sum(s["energy_kwh"] for s in sessions), 3)
        valid = [s for s in sessions if s["energy_kwh"] > 0.1]

        result = {
            "count": len(sessions),
            "total_kwh": total_kwh,
            "total_cost": round(total_kwh * price_per_kwh, 2),
            "price_per_kwh": price_per_kwh,
            "last_session_kwh": valid[0]["energy_kwh"] if valid else 0,
            "last_session_start": valid[0]["start"] if valid else None,
            "last_vehicle": valid[0]["vehicle"] if valid else "",
            "vehicles": vehicles_sorted,
            "vehicle_totals": {v: round(vehicle_totals[v], 3) for v in vehicles_sorted},
            "monthly_summary": monthly_summary,
            "sessions": sessions[:50],
        }

        with open(OUTPUT_FILE, "w") as f:
            json.dump(result, f, indent=2)

        print(json.dumps(result))

    except Exception as e:
        result = {"error": str(e), "sessions": [], "count": 0, "total_kwh": 0}
        print(json.dumps(result), file=sys.stderr)
        print(json.dumps(result))
        sys.exit(1)


if __name__ == "__main__":
    main()
