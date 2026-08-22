from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    API_EVENT_LIMIT,
    DOMAIN,
    METER_BLOCK_COUNT,
    MODBUS_CONNECT_TIMEOUT,
    MODBUS_SLAVE_ID,
    REG_CP_STATUS,
    REG_ENERGY_L1,
    REG_HEMS_CURRENT_LIMIT,
    REG_PHASE_SWITCH_MODE,
    REG_SAFE_CURRENT,
    REG_SESSION_ENERGY,
    REG_SIGNALED_CURRENT,
    REG_VEHICLE_STATE,
)

_LOGGER = logging.getLogger(__name__)


def _to_uint32(high: int, low: int) -> int:
    """Combine two registers into an unsigned 32-bit value, high word first."""
    return (high << 16) | low


def _to_int32(high: int, low: int) -> int:
    """Combine two registers into a signed 32-bit value, high word first."""
    val = (high << 16) | low
    return val - 4294967296 if val > 2147483647 else val


class ModbusDataCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, host: str, port: int, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_modbus",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._host = host
        self._port = port
        self._client = None

    async def _get_client(self):
        from pymodbus.client import AsyncModbusTcpClient

        if self._client is not None and self._client.connected:
            return self._client

        self._client = AsyncModbusTcpClient(
            self._host, port=self._port, timeout=MODBUS_CONNECT_TIMEOUT
        )
        await self._client.connect()

        # connect() can report success while the wallbox drops the session again
        # right after the TCP handshake, so the transport state is the only
        # reliable signal. Without this check the first read would fail with a
        # bare pymodbus ConnectionException traceback instead of a usable hint.
        if not self._client.connected:
            self._client = None
            raise UpdateFailed(
                f"No Modbus TCP connection to {self._host}:{self._port} — the wallbox "
                "accepted the TCP handshake and closed it again. It serves a single "
                "Modbus client at a time, so check for a second Home Assistant instance, "
                "a YAML 'modbus:' block polling the same wallbox, or an external energy "
                "manager holding the connection. Verify Modbus TCP is enabled as well."
            )

        return self._client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            client = await self._get_client()
            data: dict[str, Any] = {}

            # OCPP status (104) + error codes (105–112, 4 * uint32)
            r = await client.read_holding_registers(REG_CP_STATUS, count=9, device_id=MODBUS_SLAVE_ID)
            if not r.isError() and len(r.registers) >= 9:
                regs = r.registers
                data["cp_status"] = regs[0]
                data["error_codes"] = [
                    _to_uint32(regs[i], regs[i + 1]) for i in range(1, 9, 2)
                ]

            # Vehicle state + CP availability: 122–124 (3 registers)
            r = await client.read_holding_registers(REG_VEHICLE_STATE, count=3, device_id=MODBUS_SLAVE_ID)
            if not r.isError():
                data["vehicle_state"] = r.registers[0]
                data["cp_availability"] = r.registers[2]

            # Safe current + comm timeout: 131–132 (2 registers)
            r = await client.read_holding_registers(REG_SAFE_CURRENT, count=2, device_id=MODBUS_SLAVE_ID)
            if not r.isError():
                data["safe_current"] = r.registers[0]
                data["comm_timeout"] = r.registers[1]

            # Meter block 200–227. Every value is an int32 spread over two
            # registers, high word first. Reading only the high word (as an
            # earlier revision did) yields 0 for realistic power and voltage
            # readings, because those fit entirely into the low word.
            r = await client.read_holding_registers(
                REG_ENERGY_L1, count=METER_BLOCK_COUNT, device_id=MODBUS_SLAVE_ID
            )
            if not r.isError() and len(r.registers) >= METER_BLOCK_COUNT:
                regs = r.registers
                # Energy 200–205 [Wh] → kWh. L1 carries the meter total,
                # L2/L3 report 0 on this device family.
                data["energy_l1"] = round(_to_int32(regs[0], regs[1]) / 1000.0, 3)
                data["energy_l2"] = round(_to_int32(regs[2], regs[3]) / 1000.0, 3)
                data["energy_l3"] = round(_to_int32(regs[4], regs[5]) / 1000.0, 3)
                # Power 206–211 [W]
                data["power_l1"] = _to_int32(regs[6], regs[7])
                data["power_l2"] = _to_int32(regs[8], regs[9])
                data["power_l3"] = _to_int32(regs[10], regs[11])
                # Current 212–217 [mA] → A
                data["current_l1"] = round(_to_int32(regs[12], regs[13]) / 1000.0, 3)
                data["current_l2"] = round(_to_int32(regs[14], regs[15]) / 1000.0, 3)
                data["current_l3"] = round(_to_int32(regs[16], regs[17]) / 1000.0, 3)
                # Total energy 218–219 [Wh] → kWh
                data["total_energy"] = round(_to_int32(regs[18], regs[19]) / 1000.0, 3)
                # Total power 220–221 [W]
                data["total_power"] = _to_int32(regs[20], regs[21])
                # Voltage 222–227 [V]
                data["voltage_l1"] = _to_int32(regs[22], regs[23])
                data["voltage_l2"] = _to_int32(regs[24], regs[25])
                data["voltage_l3"] = _to_int32(regs[26], regs[27])

            # Signaled current: 706 (1 register)
            r = await client.read_holding_registers(REG_SIGNALED_CURRENT, count=1, device_id=MODBUS_SLAVE_ID)
            if not r.isError():
                data["signaled_current"] = r.registers[0]

            # Session data: 716-719 (2 x uint32)
            r = await client.read_holding_registers(REG_SESSION_ENERGY, count=4, device_id=MODBUS_SLAVE_ID)
            if not r.isError() and len(r.registers) >= 4:
                regs = r.registers
                # Charged Energy: 716-717 [Wh] → kWh
                data["session_energy"] = round(_to_uint32(regs[0], regs[1]) / 1000.0, 3)
                # Charging Duration: 718-719 [s]
                data["session_duration"] = _to_uint32(regs[2], regs[3])

            # HEMS limit (v1.5): 2000 (1 register)
            r = await client.read_holding_registers(REG_HEMS_CURRENT_LIMIT, count=1, device_id=MODBUS_SLAVE_ID)
            if not r.isError():
                data["hems_current_limit"] = r.registers[0]

            # Phase Switch Mode: 2020 (1 register)
            r = await client.read_holding_registers(REG_PHASE_SWITCH_MODE, count=1, device_id=MODBUS_SLAVE_ID)
            if not r.isError():
                data["phase_switch_mode"] = r.registers[0]

            return data

        except UpdateFailed:
            raise
        except Exception as err:
            if self._client:
                self._client.close()
                self._client = None
            raise UpdateFailed(f"Modbus communication error: {err}") from err

    async def write_register(self, address: int, value: int) -> bool:
        try:
            client = await self._get_client()
            result = await client.write_register(address, value, device_id=MODBUS_SLAVE_ID)
            return not result.isError()
        except Exception as err:
            _LOGGER.error("Failed to write register %s = %s: %s", address, value, err)
            if self._client:
                self._client.close()
                self._client = None
            return False

    async def async_close(self) -> None:
        if self._client:
            self._client.close()
            self._client = None


class WallboxApiCoordinator(DataUpdateCoordinator):
    """Base for the REST API coordinators.

    Both REST coordinators refresh on demand only — the wallbox accepts a single
    Modbus client and every REST call costs a full nonce/login round trip, so
    polling them on a timer buys nothing. Home Assistant fetches once during
    setup, afterwards the refresh buttons trigger an update.
    """

    def __init__(self, hass: HomeAssistant, name: str, host: str, api_port: int,
                 password: str) -> None:
        super().__init__(hass, _LOGGER, name=name, update_interval=None)
        self._host = host
        self._password = password
        self._base_url = f"http://{host}:{api_port}/api/v1"

    async def _authenticate(self, session: aiohttp.ClientSession) -> str:
        """Fetch a single-use nonce and exchange the installer password for a token."""
        async with session.get(f"{self._base_url}/Nonce") as r:
            r.raise_for_status()
            nonce = (await r.text()).strip().strip('"')

        async with session.post(
            f"{self._base_url}/AuthManagement/login",
            headers={"X-Nonce": nonce, "Content-Type": "application/json"},
            json={"username": "Installer", "password": self._password},
        ) as r:
            r.raise_for_status()
            payload = await r.json()
            token = payload.get("token") or payload.get("access_token", "")
            if not token:
                raise UpdateFailed("Authentication returned no token")
            return token


class SessionDataCoordinator(WallboxApiCoordinator):
    def __init__(
        self, hass: HomeAssistant, host: str, api_port: int, password: str,
        price_per_kwh: float
    ) -> None:
        super().__init__(hass, f"{DOMAIN}_sessions", host, api_port, password)
        self._price = price_per_kwh
        self._vehicles: dict[str, str] = {}
        self._raw: list = []

    def set_price(self, price: float) -> None:
        self._price = price

    @property
    def currency(self) -> str:
        """Currency of the costs: the Home Assistant currency (Settings → System → General)."""
        return self.hass.config.currency

    def set_vehicles(self, vehicles: dict[str, str]) -> None:
        self._vehicles = vehicles

    @property
    def vehicles(self) -> dict[str, str]:
        """RFID → name mapping currently in effect."""
        return self._vehicles

    def reprocess_cached(self) -> None:
        """Recompute names, costs and totals from cached data, without calling the API."""
        if self._raw:
            self.async_set_updated_data(self._process(self._raw))

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                token = await self._authenticate(session)
                self._raw = await self._fetch_sessions(session, token)
                return self._process(self._raw)
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Session API error: {err}") from err

    async def _fetch_sessions(self, session: aiohttp.ClientSession, token: str) -> list:
        async with session.get(
            f"{self._base_url}/ChargingTransactionHistory/ReadFromTo",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "skip": 0,
                "take": 100,
                "from": "2024-01-01T00:00:00.000Z",
                "to": "2099-12-31T23:59:59.000Z",
            },
        ) as r:
            r.raise_for_status()
            data = await r.json()
            if isinstance(data, list):
                return data
            return data.get("items", data.get("data", []))

    def _process(self, raw: list) -> dict[str, Any]:
        sessions = []
        for s in sorted(raw, key=lambda x: x.get("startTime", ""), reverse=True):
            rfid = s.get("rfidTag") or s.get("rfid") or ""
            energy = float(s.get("energyConsumption", s.get("energy_kwh", 0)) or 0)
            vehicle = self._vehicles.get(rfid, rfid or "Unknown")
            sessions.append({
                "rfid": rfid,
                "vehicle": vehicle,
                "energy_kwh": round(energy, 3),
                "cost": round(energy * self._price, 2),
                "start": s.get("startTime", ""),
                "end": s.get("stopTime", s.get("endTime", "")),
            })

        total_kwh = sum(s["energy_kwh"] for s in sessions)
        monthly: dict[str, Any] = {}
        vehicle_totals: dict[str, Any] = {}

        for s in sessions:
            month = s["start"][:7] if s["start"] else "Unknown"
            monthly.setdefault(month, {"kwh": 0.0, "cost": 0.0, "by_vehicle": {}})
            monthly[month]["kwh"] = round(monthly[month]["kwh"] + s["energy_kwh"], 3)
            monthly[month]["cost"] = round(monthly[month]["cost"] + s["cost"], 2)
            v = s["vehicle"]
            monthly[month]["by_vehicle"].setdefault(v, {"kwh": 0.0, "cost": 0.0})
            monthly[month]["by_vehicle"][v]["kwh"] = round(
                monthly[month]["by_vehicle"][v]["kwh"] + s["energy_kwh"], 3
            )
            monthly[month]["by_vehicle"][v]["cost"] = round(
                monthly[month]["by_vehicle"][v]["cost"] + s["cost"], 2
            )
            vehicle_totals.setdefault(v, {"kwh": 0.0, "cost": 0.0})
            vehicle_totals[v]["kwh"] = round(vehicle_totals[v]["kwh"] + s["energy_kwh"], 3)
            vehicle_totals[v]["cost"] = round(vehicle_totals[v]["cost"] + s["cost"], 2)

        return {
            "sessions": sessions,
            "total_sessions": len(sessions),
            "total_kwh": round(total_kwh, 3),
            "total_cost": round(total_kwh * self._price, 2),
            "currency": self.currency,
            "price_per_kwh": self._price,
            "monthly_summary": [
                {"month": k, **v} for k, v in sorted(monthly.items(), reverse=True)
            ],
            "vehicle_totals": vehicle_totals,
            "last_session_kwh": sessions[0]["energy_kwh"] if sessions else 0.0,
            "last_vehicle": sessions[0]["vehicle"] if sessions else "",
        }


class SystemEventsCoordinator(WallboxApiCoordinator):
    """Reads the wallbox event log over the REST API.

    Replaces the command-line sensors and shell scripts of the earlier YAML setup.
    The endpoint pages at 100 entries unless take= is given, so ask for the limit
    explicitly and report the wallbox's own total alongside.
    """

    def __init__(
        self, hass: HomeAssistant, host: str, api_port: int, password: str
    ) -> None:
        super().__init__(hass, f"{DOMAIN}_events", host, api_port, password)

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=60)
            ) as session:
                token = await self._authenticate(session)
                return await self._fetch_events(session, token)
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"System events API error: {err}") from err

    async def _fetch_events(
        self, session: aiohttp.ClientSession, token: str
    ) -> dict[str, Any]:
        async with session.get(
            f"{self._base_url}/Nonce"
        ) as r:  # the endpoint expects a fresh nonce alongside the token
            r.raise_for_status()
            nonce = (await r.text()).strip().strip('"')

        async with session.get(
            f"{self._base_url}/SystemEvents",
            headers={
                "Authorization": f"Bearer {token}",
                "X-Nonce": nonce,
                "Cache-Control": "no-cache",
            },
            params={"skip": 0, "take": API_EVENT_LIMIT},
        ) as r:
            r.raise_for_status()
            payload = await r.json()

        raw = payload.get("list", []) if isinstance(payload, dict) else []
        events = [
            {
                "timestamp": e.get("timestamp") or e.get("@t") or "",
                # parsedSeverity carries the real level; "severity" is Error for
                # every entry on protocol 1.5 firmware and cannot be used.
                "level": e.get("parsedSeverity") or "Unknown",
                "event_id": e.get("shortcutWithEventId") or "",
                "description": e.get("description") or "",
                "source": e.get("sourceContext") or "",
            }
            for e in raw
        ]
        events.sort(key=lambda e: e["timestamp"], reverse=True)

        return {
            "events": events,
            "fetched": len(events),
            "total": payload.get("count", len(events)) if isinstance(payload, dict) else len(events),
            "levels": sorted({e["level"] for e in events if e["level"]}),
            "event_ids": sorted({e["event_id"] for e in events if e["event_id"]}),
        }
