"""Data update coordinator for Mennekes AMTRON."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = 30


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

        super().__init__(
            hass,
            _LOGGER,
            name="Mennekes AMTRON",
            update_interval=timedelta(seconds=scan_interval),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from wallbox."""
        try:
            # Minimal test data
            return {
                "status": "charging",
                "power": 7400,
                "voltage": 230,
                "current": 32,
            }
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise
