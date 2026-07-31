"""Text entities: vehicle name for the RFID assignment and the event search box."""

from __future__ import annotations

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN
from .entity import build_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    device_info = build_device_info(entry, entry_data.get("public_info", {}))

    async_add_entities(
        [
            AmtronText(
                key="vehicle_name",
                name="Vehicle name",
                icon="mdi:car",
                device_info=device_info,
                entry_id=entry.entry_id,
                ui=entry_data["ui"],
            ),
            AmtronText(
                key="event_search",
                name="Event search",
                icon="mdi:magnify",
                device_info=device_info,
                entry_id=entry.entry_id,
                ui=entry_data["ui"],
            ),
        ]
    )


class AmtronText(TextEntity, RestoreEntity):
    """Free-text input held in Home Assistant, not on the wallbox."""

    _attr_has_entity_name = True
    _attr_native_max = 50
    _attr_mode = "text"

    def __init__(
        self,
        key: str,
        name: str,
        icon: str,
        device_info: DeviceInfo,
        entry_id: str,
        ui: dict,
    ) -> None:
        self._key = key
        self._ui = ui
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{entry_id}_{key}"
        self._attr_device_info = device_info
        self._attr_native_value = ""

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) and last.state not in (
            None,
            "unknown",
            "unavailable",
        ):
            self._attr_native_value = last.state
        self._ui[self._key] = self._attr_native_value

    async def async_set_value(self, value: str) -> None:
        self._attr_native_value = value
        self._ui[self._key] = value
        self.async_write_ha_state()
