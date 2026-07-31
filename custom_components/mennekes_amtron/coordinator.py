"""Data update coordinator for Mennekes AMTRON."""

import asyncio
import logging
from datetime import timedelta

from pymodbus.client import AsyncModbusTcpClient
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = 30

# Modbus Register Map
MODBUS_REGISTERS = {
    "device_id": (100, "uint16"),
    "firmware_version": (101, "uint16"),
    "device_state": (102, "uint16"),
    "charge_state": (103, "uint16"),
    "error_code": (104, "uint16"),
    "voltage_l1": (105, "uint16"),
    "voltage_l2": (106, "uint16"),
    "voltage_l3": (107, "uint16"),
    "current_l1": (108, "int16"),
    "current_l2": (109, "int16"),
    "current_l3": (110, "int16"),
    "power_l1": (111, "int32"),
    "power_l2": (113, "int32"),
    "power_l3": (115, "int32"),
    "total_power": (117, "int32"),
    "total_energy": (119, "uint32"),
    "session_energy": (121, "uint32"),
    "session_duration": (123, "uint32"),
    "hems_limit": (125, "uint16"),
    "safe_current": (126, "uint16"),
    "availability": (127, "uint16"),
    "plug_locked": (128, "uint16"),
}


class MennekesCoordinator(DataUpdateCoordinator):
    """Coordinator for Mennekes AMTRON data."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        api_port: int,
        modbus_port: int,
        password: str,
        scan_interval: int = DEFAULT_SCAN_INTERVAL,
    ) -> None:
        """Initialize the coordinator."""
        self.host = host
        self.api_port = api_port
        self.modbus_port = modbus_port
        self.password = password
        self.client = None

        super().__init__(
            hass,
            _LOGGER,
            name="Mennekes AMTRON",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from wallbox via Modbus TCP."""
        # TEMPORARY TEST DATA - scaled correctly
        test_data = {
            "device_id": 1,
            "firmware_version": 15041,
            "device_state": 1,
            "charge_state": 2,
            "error_code": 0,
            "voltage_l1": 230,  # V
            "voltage_l2": 231,  # V
            "voltage_l3": 229,  # V
            "current_l1": 32.0,  # A (÷ 1000 from mA)
            "current_l2": 31.5,  # A
            "current_l3": 32.5,  # A
            "power_l1": 7360,  # W
            "power_l2": 7265,  # W
            "power_l3": 7462,  # W
            "total_power": 22087,  # W
            "total_energy": 125.4,  # kWh (÷ 1000 from Wh)
            "session_energy": 45.3,  # kWh
            "session_duration": 3600,  # s
            "hems_limit": 32,  # A
            "safe_current": 32,  # A
            "availability": 1,
            "plug_locked": 1,
        }
        return test_data

        try:
            if not self.client:
                self.client = AsyncModbusTcpClient(
                    host=self.host, port=self.modbus_port, timeout=10
                )
                await self.client.connect()

            data = {}

            # Read all registers
            for name, (address, reg_type) in MODBUS_REGISTERS.items():
                try:
                    if "int32" in reg_type or "uint32" in reg_type:
                        result = await self.client.read_holding_registers(
                            address, 2, unit=1
                        )
                        if result.isError():
                            data[name] = 0
                        else:
                            value = (result.registers[0] << 16) | result.registers[1]
                            if "int32" in reg_type and value > 2147483647:
                                value -= 4294967296
                            data[name] = value
                    else:
                        result = await self.client.read_holding_registers(
                            address, 1, unit=1
                        )
                        if result.isError():
                            data[name] = 0
                        else:
                            value = result.registers[0]
                            if "int16" in reg_type and value > 32767:
                                value -= 65536
                            data[name] = value
                except Exception as err:
                    _LOGGER.debug("Error reading register %s: %s", name, err)
                    data[name] = 0

            return data

        except Exception as err:
            _LOGGER.error("Error updating data: %s", err)
            raise UpdateFailed(f"Error communicating with wallbox: {err}") from err

    async def async_shutdown(self) -> None:
        """Shutdown coordinator."""
        if self.client:
            await self.client.close()
