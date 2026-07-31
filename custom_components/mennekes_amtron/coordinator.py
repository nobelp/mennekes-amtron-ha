from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    MODBUS_SLAVE_ID,
    REG_CP_STATUS,
    REG_ERROR_CODE_1,
    REG_VEHICLE_STATE,
    REG_CP_AVAILABILITY,
    REG_SAFE_CURRENT,
    REG_COMM_TIMEOUT,
    REG_ENERGY_L1,
    REG_POWER_L1,
    REG_CURRENT_L1,
    REG_VOLTAGE_L1,
    REG_SIGNALED_CURRENT,
    REG_SESSION_ENERGY,
    REG_SESSION_DURATION,
    REG_HEMS_CURRENT_LIMIT,
    REG_PHASE_SWITCH_MODE,
)

_LOGGER = logging.getLogger(__name__)


def _to_int16(val: int) -> int:
    return val - 65536 if val > 32767 else val


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
        if self._client is None or not self._client.connected:
            self._client = AsyncModbusTcpClient(
                host=self._host,
                port=self._port,
                timeout=5
            )
            await self._client.connect()
        return self._client

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            client = await self._get_client()
            data: dict[str, Any] = {}

            _LOGGER.debug("Reading Modbus registers from %s:%d", self._host, self._port)

            # CP status + error codes: 104–108 (5 registers)
            r = await client.read_holding_registers(REG_CP_STATUS, count=5, unit=MODBUS_SLAVE_ID)
            if not r.isError():
                data["cp_status"] = r.registers[0]
                data["error_codes"] = r.registers[1:5]

            # Vehicle state + CP availability: 122–124 (3 registers)
            r = await client.read_holding_registers(REG_VEHICLE_STATE, count=3, slave=MODBUS_SLAVE_ID)
            if not r.isError():
                data["vehicle_state"] = r.registers[0]
                data["cp_availability"] = r.registers[2]

            # Safe current + comm timeout: 131–132 (2 registers)
            r = await client.read_holding_registers(REG_SAFE_CURRENT, count=2, slave=MODBUS_SLAVE_ID)
            if not r.isError():
                data["safe_current"] = r.registers[0]
                data["comm_timeout"] = r.registers[1]

            # Meter Energy/Power/Current/Voltage: 200–227 (28 registers)
            # Each value is int32 (2 registers): L1, L2, L3 for each measurement
            r = await client.read_holding_registers(REG_ENERGY_L1, count=28, slave=MODBUS_SLAVE_ID)
            if not r.isError():
                regs = r.registers
                # Energy: 200-205 (3 x int32)
                data["energy_l1"] = round((regs[1] << 16 | regs[0]) / 1000.0, 3) if len(regs) > 1 else 0
                data["energy_l2"] = round((regs[3] << 16 | regs[2]) / 1000.0, 3) if len(regs) > 3 else 0
                data["energy_l3"] = round((regs[5] << 16 | regs[4]) / 1000.0, 3) if len(regs) > 5 else 0
                # Power: 206-211 (3 x int32)
                data["power_l1"] = _to_int16(regs[6]) if len(regs) > 6 else 0
                data["power_l2"] = _to_int16(regs[8]) if len(regs) > 8 else 0
                data["power_l3"] = _to_int16(regs[10]) if len(regs) > 10 else 0
                # Current: 212-217 (3 x int32, in mA)
                data["current_l1"] = round((regs[13] << 16 | regs[12]) / 1000.0, 3) if len(regs) > 13 else 0
                data["current_l2"] = round((regs[15] << 16 | regs[14]) / 1000.0, 3) if len(regs) > 15 else 0
                data["current_l3"] = round((regs[17] << 16 | regs[16]) / 1000.0, 3) if len(regs) > 17 else 0
                # Total Energy: 218-219 (1 x int32)
                data["total_energy"] = round((regs[19] << 16 | regs[18]) / 1000.0, 3) if len(regs) > 19 else 0
                # Total Power: 220-221 (1 x int32)
                data["total_power"] = _to_int16(regs[20]) if len(regs) > 20 else 0
                # Voltage: 222-227 (3 x int32)
                data["voltage_l1"] = regs[22] if len(regs) > 22 else 0
                data["voltage_l2"] = regs[24] if len(regs) > 24 else 0
                data["voltage_l3"] = regs[26] if len(regs) > 26 else 0

            # Signaled current: 706 (1 register)
            r = await client.read_holding_registers(REG_SIGNALED_CURRENT, count=1, slave=MODBUS_SLAVE_ID)
            if not r.isError():
                data["signaled_current"] = r.registers[0]

            # Session data: 716-719 (4 registers)
            r = await client.read_holding_registers(REG_SESSION_ENERGY, count=4, slave=MODBUS_SLAVE_ID)
            if not r.isError():
                regs = r.registers
                # Charged Energy: 716-717 (1 x uint32)
                data["session_energy"] = round((regs[1] << 16 | regs[0]) / 1000.0, 3)
                # Charging Duration: 718-719 (1 x uint32, in seconds)
                data["session_duration"] = (regs[3] << 16) | regs[2]

            # HEMS limit (v1.5): 2000 (1 register)
            r = await client.read_holding_registers(REG_HEMS_CURRENT_LIMIT, count=1, slave=MODBUS_SLAVE_ID)
            if not r.isError():
                data["hems_current_limit"] = r.registers[0]

            # Phase Switch Mode: 2020 (1 register)
            r = await client.read_holding_registers(REG_PHASE_SWITCH_MODE, count=1, slave=MODBUS_SLAVE_ID)
            if not r.isError():
                data["phase_switch_mode"] = r.registers[0]

            _LOGGER.debug("Successfully read %d registers", len(data))
            return data

        except Exception as err:
            _LOGGER.error("Modbus communication error: %s", err, exc_info=True)
            if self._client:
                self._client.close()
                self._client = None
            raise UpdateFailed(f"Modbus communication error: {err}") from err

    async def write_register(self, address: int, value: int) -> bool:
        try:
            client = await self._get_client()
            result = await client.write_register(address, value, unit=MODBUS_SLAVE_ID)
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


class SessionDataCoordinator(DataUpdateCoordinator):
    def __init__(
        self, hass: HomeAssistant, host: str, password: str, price_per_kwh: float
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_sessions",
            update_interval=timedelta(hours=1),
        )
        self._host = host
        self._password = password
        self._price = price_per_kwh
        self._base_url = f"http://{host}/api/v1"
        self._vehicles: dict[str, str] = {}

    def set_price(self, price: float) -> None:
        self._price = price

    def set_vehicles(self, vehicles: dict[str, str]) -> None:
        self._vehicles = vehicles

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            ) as session:
                token = await self._authenticate(session)
                raw = await self._fetch_sessions(session, token)
                return self._process(raw)
        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Session API error: {err}") from err

    async def _authenticate(self, session: aiohttp.ClientSession) -> str:
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
                "cost_chf": round(energy * self._price, 2),
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
            monthly[month]["cost"] = round(monthly[month]["cost"] + s["cost_chf"], 2)
            v = s["vehicle"]
            monthly[month]["by_vehicle"].setdefault(v, {"kwh": 0.0, "cost": 0.0})
            monthly[month]["by_vehicle"][v]["kwh"] = round(
                monthly[month]["by_vehicle"][v]["kwh"] + s["energy_kwh"], 3
            )
            monthly[month]["by_vehicle"][v]["cost"] = round(
                monthly[month]["by_vehicle"][v]["cost"] + s["cost_chf"], 2
            )
            vehicle_totals.setdefault(v, {"kwh": 0.0, "cost": 0.0})
            vehicle_totals[v]["kwh"] = round(vehicle_totals[v]["kwh"] + s["energy_kwh"], 3)
            vehicle_totals[v]["cost"] = round(vehicle_totals[v]["cost"] + s["cost_chf"], 2)

        return {
            "sessions": sessions,
            "total_sessions": len(sessions),
            "total_kwh": round(total_kwh, 3),
            "total_cost": round(total_kwh * self._price, 2),
            "monthly_summary": [
                {"month": k, **v} for k, v in sorted(monthly.items(), reverse=True)
            ],
            "vehicle_totals": vehicle_totals,
            "last_session_kwh": sessions[0]["energy_kwh"] if sessions else 0.0,
            "last_vehicle": sessions[0]["vehicle"] if sessions else "",
        }
