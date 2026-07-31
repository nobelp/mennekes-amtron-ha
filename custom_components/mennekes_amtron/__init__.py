from __future__ import annotations

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_WALLBOX_HOST]
    modbus_port = entry.data.get(CONF_MODBUS_PORT, DEFAULT_MODBUS_PORT)
    api_port = entry.data.get(CONF_API_PORT, DEFAULT_API_PORT)
    api_password = entry.data[CONF_API_PASSWORD]
    price = entry.data.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    public_info = await _fetch_public_info(host, api_port)

    vehicles: dict[str, str] = dict(entry.options.get(CONF_VEHICLES, {}))

    modbus_coord = ModbusDataCoordinator(hass, host, modbus_port, scan_interval)
    session_coord = SessionDataCoordinator(hass, host, api_port, api_password, price)
    session_coord.set_vehicles(vehicles)
    events_coord = SystemEventsCoordinator(hass, host, api_port, api_password)

    await modbus_coord.async_config_entry_first_refresh()

    # Both REST data sets are non-critical and refresh on demand afterwards –
    # never block setup on API failures.
    for coordinator in (session_coord, events_coord):
        try:
            await coordinator.async_config_entry_first_refresh()
        except Exception:  # setup must survive any API problem
            pass

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
    return True


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
            session_coord.reapply_vehicles()
            return

    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinators = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinators["modbus"].async_close()
    return unload_ok
