"""Select entities: RFID picker and the system-event filters."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EVENT_LEVELS, FILTER_ALL
from .coordinator import SessionDataCoordinator, SystemEventsCoordinator
from .entity import build_device_info


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    entry_data = hass.data[DOMAIN][entry.entry_id]
    device_info = build_device_info(entry, entry_data.get("public_info", {}))

    async_add_entities(
        [
            RfidSelect(
                entry_data["sessions"], device_info, entry.entry_id, entry_data["ui"]
            ),
            EventIdSelect(entry_data["events"], device_info, entry.entry_id),
            EventLevelSelect(device_info, entry.entry_id),
        ]
    )


class RfidSelect(CoordinatorEntity[SessionDataCoordinator], SelectEntity):
    """Lists the RFID tags seen in the charging history, newest session first."""

    _attr_has_entity_name = True
    _attr_name = "RFID"
    _attr_icon = "mdi:card-account-details-outline"

    def __init__(
        self,
        coordinator: SessionDataCoordinator,
        device_info: DeviceInfo,
        entry_id: str,
        ui: dict,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_rfid_select"
        self._attr_device_info = device_info
        self._ui = ui
        self._selected: str | None = None

    @property
    def options(self) -> list[str]:
        data = self.coordinator.data or {}
        tags: list[str] = []
        for session in data.get("sessions", []):
            tag = session.get("rfid")
            if tag and tag not in tags:
                tags.append(tag)
        # Keep already assigned tags selectable even when they drop out of the
        # fetched history window.
        for tag in data.get("vehicle_totals", {}):
            if tag not in tags:
                tags.append(tag)
        return tags or [FILTER_ALL]

    @property
    def current_option(self) -> str | None:
        options = self.options
        if self._selected in options:
            return self._selected
        return options[0] if options else None

    async def async_select_option(self, option: str) -> None:
        self._selected = option
        self._ui["rfid"] = option
        self.async_write_ha_state()


class EventIdSelect(CoordinatorEntity[SystemEventsCoordinator], SelectEntity):
    """Event-ID filter for the system events view; options follow the fetched log."""

    _attr_has_entity_name = True
    _attr_name = "Event ID filter"
    _attr_icon = "mdi:tag-outline"

    def __init__(
        self,
        coordinator: SystemEventsCoordinator,
        device_info: DeviceInfo,
        entry_id: str,
    ) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry_id}_event_id_filter"
        self._attr_device_info = device_info
        self._selected = FILTER_ALL

    @property
    def options(self) -> list[str]:
        data = self.coordinator.data or {}
        return [FILTER_ALL, *data.get("event_ids", [])]

    @property
    def current_option(self) -> str:
        return self._selected if self._selected in self.options else FILTER_ALL

    async def async_select_option(self, option: str) -> None:
        self._selected = option
        self.async_write_ha_state()


class EventLevelSelect(SelectEntity, RestoreEntity):
    """Severity filter. Fixed options, so the choice survives a restart."""

    _attr_has_entity_name = True
    _attr_name = "Event level filter"
    _attr_icon = "mdi:alert-circle-outline"

    def __init__(self, device_info: DeviceInfo, entry_id: str) -> None:
        self._attr_unique_id = f"{entry_id}_event_level_filter"
        self._attr_device_info = device_info
        self._attr_options = list(EVENT_LEVELS)
        self._attr_current_option = FILTER_ALL

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        if (last := await self.async_get_last_state()) and last.state in self._attr_options:
            self._attr_current_option = last.state

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()
