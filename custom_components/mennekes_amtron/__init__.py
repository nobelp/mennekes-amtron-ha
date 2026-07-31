"""Mennekes AMTRON Wallbox integration for Home Assistant."""

DOMAIN = "mennekes_amtron"
VERSION = "1.2.0"


async def async_setup(hass, config):
    """Set up the Mennekes AMTRON integration."""
    hass.data[DOMAIN] = {}
    return True
