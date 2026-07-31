from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfElectricCurrent, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    MANUFACTURER,
    MODEL,
    REG_HEMS_CURRENT_LIMIT,
    REG_SAFE_CURRENT,
    REG_COMM_TIMEOUT,
)
from .coordinator import ModbusDataCoordinator


@dataclass(frozen=True, kw_only=True)
class AmtronNumberDescription(NumberEntityDescription):
    register: int = 0
    data_key: str = ""


NUMBER_DESCRIPTIONS: tuple[AmtronNumberDescription, ...] = (
    AmtronNumberDescription(
        key="hems_current_limit",
        name="HEMS Current Limit",
        native_min_value=0,
        native_max_value=16,
        native_step=1,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        mode=NumberMode.SLIDER,
        register=REG_HEMS_CURRENT_LIMIT,
        data_key="hems_current_limit",
    ),
    AmtronNumberDescription(
        key="safe_current",
        name="Safe Current",
        native_min_value=0,
        native_max_value=32,
        native_step=1,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        mode=NumberMode.SLIDER,
        register=REG_SAFE_CURRENT,
        data_key="safe_current",
    ),
    AmtronNumberDescription(
        key="comm_timeout",
        name="Communication Timeout",
        native_min_value=1,
        native_max_value=300,
        native_step=1,
        native_unit_of_measurement=UnitOfTime.SECONDS,
        mode=NumberMode.BOX,
        register=REG_COMM_TIMEOUT,
        data_key="comm_timeout",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator: ModbusDataCoordinator = entry_data["modbus"]
    public_info: dict = entry_data.get("public_info", {})

    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Mennekes AMTRON",
        manufacturer=MANUFACTURER,
        model=public_info.get("articleName", MODEL),
        sw_version=public_info.get("currentVersion"),
        serial_number=public_info.get("serialNumber"),
    )

    async_add_entities(
        AmtronNumber(coordinator, description, device_info, entry.entry_id)
        for description in NUMBER_DESCRIPTIONS
    )


class AmtronNumber(CoordinatorEntity[ModbusDataCoordinator], NumberEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: ModbusDataCoordinator,
        description: AmtronNumberDescription,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry_id}_{description.key}"
        self._attr_device_info = device_info

    @property
    def native_value(self) -> float | None:
        if not self.coordinator.data:
            return None
        return self.coordinator.data.get(self.entity_description.data_key)

    async def async_set_native_value(self, value: float) -> None:
        desc = self.entity_description
        success = await self.coordinator.write_register(desc.register, int(value))
        if success:
            await self.coordinator.async_request_refresh()
