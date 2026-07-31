"""Buttons: assign a vehicle to an RFID tag and refresh the two REST data sets."""

from __future__ import annotations

import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_VEHICLES, DOMAIN
from .entity import build_device_info

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    device_info = build_device_info(entry, entry_data.get("public_info", {}))

    async_add_entities(
        [
            AssignVehicleButton(hass, entry, device_info),
            RefreshHistoryButton(hass, entry, device_info),
            RefreshEventsButton(hass, entry, device_info),
        ]
    )


class _AmtronButton(ButtonEntity):
    _attr_has_entity_name = True
    _key = ""

    def __init__(
        self, hass: HomeAssistant, entry: ConfigEntry, device_info: DeviceInfo
    ) -> None:
        self.hass = hass
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{self._key}"
        self._attr_device_info = device_info

    @property
    def _entry_data(self) -> dict:
        return self.hass.data[DOMAIN][self._entry.entry_id]


class AssignVehicleButton(_AmtronButton):
    """Stores RFID → name in the config entry options and re-labels the history."""

    _key = "assign_vehicle"
    _attr_name = "Assign vehicle"
    _attr_icon = "mdi:account-check-outline"

    async def async_press(self) -> None:
        ui = self._entry_data["ui"]
        rfid = (ui.get("rfid") or "").strip()
        name = (ui.get("vehicle_name") or "").strip()
        if not rfid or not name:
            _LOGGER.warning(
                "Assign vehicle needs both an RFID tag and a name (got %r / %r)",
                rfid,
                name,
            )
            return

        vehicles = dict(self._entry.options.get(CONF_VEHICLES, {}))
        vehicles[rfid] = name
        self.hass.config_entries.async_update_entry(
            self._entry, options={**self._entry.options, CONF_VEHICLES: vehicles}
        )
        _LOGGER.info("Assigned RFID %s to %s", rfid, name)


class RefreshHistoryButton(_AmtronButton):
    """The charging history is fetched on demand only — this triggers it."""

    _key = "refresh_history"
    _attr_name = "Refresh charging history"
    _attr_icon = "mdi:history"

    async def async_press(self) -> None:
        await self._entry_data["sessions"].async_request_refresh()


class RefreshEventsButton(_AmtronButton):
    _key = "refresh_events"
    _attr_name = "Refresh system events"
    _attr_icon = "mdi:refresh"

    async def async_press(self) -> None:
        await self._entry_data["events"].async_request_refresh()
