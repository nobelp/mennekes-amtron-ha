from __future__ import annotations

from typing import Any

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_CORE_CONFIG_UPDATE, Platform
from homeassistant.core import Event, HomeAssistant, callback

from .const import (
    DOMAIN,
    CONF_VEHICLES,
    CONF_WALLBOX_HOST,
    CONF_MODBUS_PORT,
    CONF_API_PORT,
    CONF_API_PASSWORD,
    CONF_PRICE_PER_KWH,
    CONF_SCAN_INTERVAL,
    DEFAULT_MODBUS_PORT,
    DEFAULT_API_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_PRICE_PER_KWH,
)
from .coordinator import (
    ModbusDataCoordinator,
    SessionDataCoordinator,
    SystemEventsCoordinator,
    WallboxApiCoordinator,
)

PLATFORMS = [
    Platform.SENSOR,
    Platform.NUMBER,
    Platform.SWITCH,
    Platform.SELECT,
    Platform.TEXT,
    Platform.BUTTON,
]


async def _fetch_public_info(host: str, api_port: int = DEFAULT_API_PORT) -> dict:
    """Fetch device info from unauthenticated PublicInfo endpoint."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(f"http://{host}:{api_port}/api/v1/PublicInfo") as r:
                if r.status == 200:
                    return await r.json()
    except Exception:
        pass
    return {}


def _setting(entry: ConfigEntry, key: str, default: Any) -> Any:
    """Return an entry setting, preferring the options over the initial data."""
    return entry.options.get(key, entry.data.get(key, default))


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_WALLBOX_HOST]
    modbus_port = entry.data.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT)
    api_port = entry.data.get(CONF_API_PORT, DEFAULT_API_PORT)
    api_password = entry.data[CONF_API_PASSWORD]
    # Price and interval can be changed later via the options flow, so the
    # options win over the values entered during the initial setup.
    price = _setting(entry, CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH)
    scan_interval = _setting(entry, CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    public_info = await _fetch_public_info(host, api_port)

    vehicles: dict[str, str] = dict(entry.options.get(CONF_VEHICLES, {}))

    modbus_coord = ModbusDataCoordinator(hass, host, modbus_port, scan_interval)
    session_coord = SessionDataCoordinator(hass, host, api_port, api_password, price)
    session_coord.set_vehicles(vehicles)
    events_coord = SystemEventsCoordinator(hass, host, api_port, api_password)

    await modbus_coord.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "modbus": modbus_coord,
        "sessions": session_coord,
        "events": events_coord,
        "public_info": public_info,
        "vehicles": vehicles,
        # Shared state of the RFID picker and the text inputs, read by the buttons.
        "ui": {"rfid": None, "vehicle_name": "", "event_search": ""},
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    # Costs are reported in the Home Assistant currency. Re-label the cached
    # history when it changes so the unit follows without a restart.
    @callback
    def _core_config_updated(_: Event) -> None:
        session_coord.reprocess_cached()

    entry.async_on_unload(
        hass.bus.async_listen(EVENT_CORE_CONFIG_UPDATE, _core_config_updated)
    )

    # The REST data sets are non-critical and refresh on demand afterwards, so
    # they must never delay or abort the setup. A slow wallbox web service used
    # to hold the setup for up to 90 s and, when it was cancelled meanwhile,
    # left every entity unavailable although Modbus worked. The coordinators
    # report failures themselves; a rejected password starts the
    # re-authentication flow.
    entry.async_create_background_task(
        hass,
        _async_load_rest_data(session_coord, events_coord),
        name=f"{DOMAIN}_initial_rest_refresh",
    )
    return True


async def _async_load_rest_data(*coordinators: WallboxApiCoordinator) -> None:
    """Fetch the REST data one after another, as the wallbox serves requests slowly."""
    for coordinator in coordinators:
        await coordinator.async_refresh()


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """React to option changes.

    Assigning a vehicle only changes the RFID mapping. Reloading the entry for that
    would drop and reopen the Modbus connection, which the wallbox only grants to a
    single client — so re-label the cached history instead and reload for everything
    else.
    """
    entry_data = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if entry_data is not None:
        vehicles = dict(entry.options.get(CONF_VEHICLES, {}))
        if vehicles != entry_data.get("vehicles"):
            entry_data["vehicles"] = vehicles
            session_coord: SessionDataCoordinator = entry_data["sessions"]
            session_coord.set_vehicles(vehicles)
            session_coord.reprocess_cached()
            return

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinators = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinators["modbus"].async_close()
    return unload_ok
