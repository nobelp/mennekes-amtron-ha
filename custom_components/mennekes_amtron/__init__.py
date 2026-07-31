from __future__ import annotations

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    DOMAIN,
    CONF_WALLBOX_HOST,
    CONF_MODBUS_PORT,
    CONF_API_PASSWORD,
    CONF_PRICE_PER_KWH,
    CONF_SCAN_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_PRICE_PER_KWH,
)
from .coordinator import ModbusDataCoordinator, SessionDataCoordinator

PLATFORMS = [Platform.SENSOR, Platform.NUMBER, Platform.SWITCH]


async def _fetch_public_info(host: str) -> dict:
    """Fetch device info from unauthenticated PublicInfo endpoint."""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
            async with session.get(f"http://{host}/api/v1/PublicInfo") as r:
                if r.status == 200:
                    return await r.json()
    except Exception:
        pass
    return {}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    host = entry.data[CONF_WALLBOX_HOST]
    modbus_port = entry.data[CONF_MODBUS_PORT]
    api_password = entry.data[CONF_API_PASSWORD]
    price = entry.data.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH)
    scan_interval = entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)

    public_info = await _fetch_public_info(host)

    modbus_coord = ModbusDataCoordinator(hass, host, modbus_port, scan_interval)
    session_coord = SessionDataCoordinator(hass, host, api_password, price)

    await modbus_coord.async_config_entry_first_refresh()

    # Sessions are non-critical – don't block setup on API failures
    try:
        await session_coord.async_config_entry_first_refresh()
    except Exception:
        pass

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "modbus": modbus_coord,
        "sessions": session_coord,
        "public_info": public_info,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinators = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinators["modbus"].async_close()
    return unload_ok
