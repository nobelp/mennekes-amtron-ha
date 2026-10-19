from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, REG_HEMS_CURRENT_LIMIT
from .coordinator import ModbusDataCoordinator


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

    # The CP availability switch was removed (register 124 is read-only in protocol 1.5).
    # Drop its registry entry so it does not linger as an unavailable entity.
    registry = er.async_get(hass)
    stale_entity_id = registry.async_get_entity_id(
        "switch", DOMAIN, f"{entry.entry_id}_cp_availability"
    )
    if stale_entity_id:
        registry.async_remove(stale_entity_id)

    async_add_entities([
        PauseChargingSwitch(coordinator, device_info, entry.entry_id),
    ])


class PauseChargingSwitch(CoordinatorEntity[ModbusDataCoordinator], SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Pause Charging"
    _attr_icon = "mdi:pause-circle"

    def __init__(self, coordinator, device_info, entry_id) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_pause_charging"
        self._attr_device_info = device_info

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        # Pause = HEMS limit set to 0
        return self.coordinator.data.get("hems_current_limit", 1) == 0

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.write_register(REG_HEMS_CURRENT_LIMIT, 0)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.write_register(REG_HEMS_CURRENT_LIMIT, 16)
        await self.coordinator.async_request_refresh()
