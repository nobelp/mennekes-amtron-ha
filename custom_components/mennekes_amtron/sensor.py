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


SENSOR_MAP = [
    # System Info
    ("device_id", "Device ID", None, None),
    ("firmware_version", "Firmware Version", None, None),
    ("device_state", "Device State", None, None),
    ("error_code", "Error Code", None, None),

    # Voltages
    ("voltage_l1", "Voltage L1", "V", SensorStateClass.MEASUREMENT),
    ("voltage_l2", "Voltage L2", "V", SensorStateClass.MEASUREMENT),
    ("voltage_l3", "Voltage L3", "V", SensorStateClass.MEASUREMENT),

    # Currents (A - scaled from mA)
    ("current_l1", "Current L1", "A", SensorStateClass.MEASUREMENT),
    ("current_l2", "Current L2", "A", SensorStateClass.MEASUREMENT),
    ("current_l3", "Current L3", "A", SensorStateClass.MEASUREMENT),

    # Power (W)
    ("power_l1", "Power L1", "W", SensorStateClass.MEASUREMENT),
    ("power_l2", "Power L2", "W", SensorStateClass.MEASUREMENT),
    ("power_l3", "Power L3", "W", SensorStateClass.MEASUREMENT),
    ("total_power", "Total Power", "W", SensorStateClass.MEASUREMENT),

    # Energy (kWh - scaled from Wh)
    ("total_energy", "Total Energy", "kWh", SensorStateClass.TOTAL_INCREASING),
    ("session_energy", "Session Energy", "kWh", SensorStateClass.TOTAL_INCREASING),

    # Charging
    ("charge_state", "Charge State", None, None),
    ("session_duration", "Session Duration", "s", SensorStateClass.MEASUREMENT),

    # Control
    ("hems_limit", "HEMS Limit", "A", SensorStateClass.MEASUREMENT),
    ("safe_current", "Safe Current", "A", SensorStateClass.MEASUREMENT),
    ("availability", "Availability", None, None),
    ("plug_locked", "Plug Locked", None, None),
]


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
        MennekesSensor(coordinator, entry, key, name, unit, state_class)
        for key, name, unit, state_class in SENSOR_MAP
    ]

    async_add_entities(sensors)


class MennekesSensor(CoordinatorEntity, SensorEntity):
    """Generic Mennekes sensor."""

    def __init__(
        self,
        coordinator: MennekesCoordinator,
        entry: ConfigEntry,
        key: str,
        name: str,
        unit: str | None,
        state_class: str | None,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = f"Wallbox {name}"

        if unit:
            self._attr_native_unit_of_measurement = unit
        if state_class:
            self._attr_state_class = state_class

    @property
    def native_value(self):
        """Return the value."""
        return self.coordinator.data.get(self._key, 0)
