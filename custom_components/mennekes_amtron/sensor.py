"""Sensor entities for Mennekes AMTRON."""

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MennekesCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    coordinator: MennekesCoordinator = hass.data[DOMAIN][entry.entry_id][
        "coordinator"
    ]

    sensors = [
        MennekesStatusSensor(coordinator, entry),
        MennekesPowerSensor(coordinator, entry),
    ]

    async_add_entities(sensors)


class MennekesStatusSensor(CoordinatorEntity, SensorEntity):
    """Status sensor."""

    def __init__(self, coordinator: MennekesCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_name = "Wallbox Status"

    @property
    def native_value(self) -> str:
        """Return the status."""
        return self.coordinator.data.get("status", "unknown")


class MennekesPowerSensor(CoordinatorEntity, SensorEntity):
    """Power sensor."""

    def __init__(self, coordinator: MennekesCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_power"
        self._attr_name = "Wallbox Power"
        self._attr_native_unit_of_measurement = "W"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the power."""
        return self.coordinator.data.get("power", 0)
