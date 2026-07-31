from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CP_STATUS_MAP,
    DOMAIN,
    VEHICLE_STATE_MAP,
)
from .coordinator import (
    ModbusDataCoordinator,
    SessionDataCoordinator,
    SystemEventsCoordinator,
)
from .entity import build_device_info


@dataclass(frozen=True, kw_only=True)
class AmtronSensorDescription(SensorEntityDescription):
    value_fn: Any = None
    attr_fn: Any = None


MODBUS_SENSORS: tuple[AmtronSensorDescription, ...] = (
    AmtronSensorDescription(
        key="voltage_l1",
        name="Voltage L1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="voltage_l2",
        name="Voltage L2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="voltage_l3",
        name="Voltage L3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="current_l1",
        name="Current L1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="current_l2",
        name="Current L2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="current_l3",
        name="Current L3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="power_l1",
        name="Power L1",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="power_l2",
        name="Power L2",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="power_l3",
        name="Power L3",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="total_power",
        name="Total Power",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="energy_l1",
        name="Energy L1",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AmtronSensorDescription(
        key="energy_l2",
        name="Energy L2",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AmtronSensorDescription(
        key="energy_l3",
        name="Energy L3",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AmtronSensorDescription(
        key="total_energy",
        name="Total Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AmtronSensorDescription(
        key="session_energy",
        name="Session Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    AmtronSensorDescription(
        key="session_duration",
        name="Session Duration",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="signaled_current",
        name="Signaled Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="max_current_ev",
        name="Max Current EV",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="cp_status",
        name="Charging Status",
        value_fn=lambda d: CP_STATUS_MAP.get(d.get("cp_status", 0), "Unknown"),
    ),
    AmtronSensorDescription(
        key="vehicle_state",
        name="Vehicle State",
        value_fn=lambda d: VEHICLE_STATE_MAP.get(d.get("vehicle_state", 0), "Unknown"),
    ),
    AmtronSensorDescription(
        key="hems_current_limit",
        name="HEMS Current Limit",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="safe_current",
        name="Safe Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    AmtronSensorDescription(
        key="phase_switch_mode",
        name="Phase Switch Mode",
        value_fn=lambda d: {
            0: "1-Phase Only",
            1: "3-Phase Only",
            2: "Dynamic Phase Switch",
            3: "Static (Start-Of-Session)",
        }.get(d.get("phase_switch_mode", 0), "Unknown"),
    ),
)

SESSION_SENSORS: tuple[AmtronSensorDescription, ...] = (
    AmtronSensorDescription(
        key="total_sessions",
        name="Total Sessions",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AmtronSensorDescription(
        key="total_kwh",
        name="Total Charged Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AmtronSensorDescription(
        key="total_cost",
        name="Total Cost",
        native_unit_of_measurement="CHF",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    AmtronSensorDescription(
        key="last_session_kwh",
        name="Last Session Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL,
    ),
    AmtronSensorDescription(
        key="last_vehicle",
        name="Last Vehicle",
    ),
    AmtronSensorDescription(
        key="sessions_summary",
        name="Sessions Summary",
        value_fn=lambda d: d.get("total_sessions", 0),
        attr_fn=lambda d: {
            "sessions": d.get("sessions", [])[:20],
            "monthly_summary": d.get("monthly_summary", []),
            "vehicle_totals": d.get("vehicle_totals", {}),
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    modbus_coord: ModbusDataCoordinator = entry_data["modbus"]
    session_coord: SessionDataCoordinator = entry_data["sessions"]
    events_coord: SystemEventsCoordinator = entry_data["events"]

    device_info = build_device_info(entry, entry_data.get("public_info", {}))

    entities: list[SensorEntity] = [
        ModbusSensor(modbus_coord, description, device_info, entry.entry_id)
        for description in MODBUS_SENSORS
    ]
    entities += [
        SessionSensor(session_coord, description, device_info, entry.entry_id)
        for description in SESSION_SENSORS
    ]
    entities.append(SystemEventsSensor(events_coord, device_info, entry.entry_id))
    entities.append(KnownVehiclesSensor(session_coord, device_info, entry.entry_id))

    async_add_entities(entities)


class ModbusSensor(CoordinatorEntity[ModbusDataCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ModbusDataCoordinator,
        description: AmtronSensorDescription,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        desc = self.entity_description
        if desc.value_fn:
            return desc.value_fn(self.coordinator.data)
        return self.coordinator.data.get(desc.key)

    @property
    def extra_state_attributes(self):
        desc = self.entity_description
        if desc.attr_fn and self.coordinator.data:
            return desc.attr_fn(self.coordinator.data)
        if desc.key == "cp_status" and self.coordinator.data:
            return {"error_codes": self.coordinator.data.get("error_codes", [])}
        return None


class SessionSensor(CoordinatorEntity[SessionDataCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: SessionDataCoordinator,
        description: AmtronSensorDescription,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        desc = self.entity_description
        if desc.value_fn:
            return desc.value_fn(self.coordinator.data)
        return self.coordinator.data.get(desc.key)

    @property
    def extra_state_attributes(self):
        desc = self.entity_description
        if desc.attr_fn and self.coordinator.data:
            return desc.attr_fn(self.coordinator.data)
        return None


class SystemEventsSensor(CoordinatorEntity[SystemEventsCoordinator], SensorEntity):
    """Event log of the wallbox. The list lives in the attributes for the dashboard."""

    _attr_has_entity_name = True
    _attr_name = "System Events"
    _attr_icon = "mdi:text-box-search-outline"

    def __init__(
        self,
        coordinator: SystemEventsCoordinator,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_system_events"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> int | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get("total")

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        data = self.coordinator.data
        if not data:
            return None
        return {
            "events": data.get("events", []),
            "fetched": data.get("fetched", 0),
            "levels": data.get("levels", []),
            "event_ids": data.get("event_ids", []),
        }


class KnownVehiclesSensor(CoordinatorEntity[SessionDataCoordinator], SensorEntity):
    """RFID tags that have a name assigned, for the configuration view."""

    _attr_has_entity_name = True
    _attr_name = "Known Vehicles"
    _attr_icon = "mdi:car-multiple"

    def __init__(
        self,
        coordinator: SessionDataCoordinator,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_known_vehicles"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> int:
        return len(self.coordinator.vehicles)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "vehicles": dict(self.coordinator.vehicles),
            "vehicle_totals": (self.coordinator.data or {}).get("vehicle_totals", {}),
        }
