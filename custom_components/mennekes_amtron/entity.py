"""Shared device info for all Mennekes AMTRON platforms."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import CONF_WALLBOX_HOST, DOMAIN, MANUFACTURER, MODEL


def build_device_info(entry: ConfigEntry, public_info: dict) -> DeviceInfo:
    """Describe the wallbox as one device.

    Model, firmware and serial come from the wallbox itself via PublicInfo, so the
    same integration covers the whole 4You / 4Business range without configuration.
    """
    return DeviceInfo(
        identifiers={(DOMAIN, entry.entry_id)},
        name="Mennekes AMTRON",
        manufacturer=MANUFACTURER,
        model=public_info.get("articleName", MODEL),
        sw_version=public_info.get("currentVersion"),
        serial_number=public_info.get("serialNumber"),
        configuration_url=f"http://{entry.data[CONF_WALLBOX_HOST]}",
    )
