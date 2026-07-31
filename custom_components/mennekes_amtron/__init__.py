"""Mennekes AMTRON Wallbox integration for Home Assistant."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN

VERSION = "1.3.0"

PLATFORMS = []


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Mennekes AMTRON integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Mennekes AMTRON from a config entry."""
    hass.data[DOMAIN][entry.entry_id] = {
        "host": entry.data.get("host"),
        "api_port": entry.data.get("api_port", 80),
        "password": entry.data.get("password"),
        "modbus_port": entry.data.get("modbus_port", 502),
        "electricity_price": entry.data.get("electricity_price", 0.29),
        "scan_interval": entry.data.get("scan_interval", 30),
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)
    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
