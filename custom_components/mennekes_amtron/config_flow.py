"""Config flow for Mennekes AMTRON Wallbox integration."""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class MennekesConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Mennekes AMTRON."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Simple validation - no HTTP calls
            host = user_input.get("host", "").strip()
            port = user_input.get("api_port", 80)

            if not host:
                errors["host"] = "host_required"
            elif not (1 <= port <= 65535):
                errors["api_port"] = "invalid_port"
            elif not user_input.get("password"):
                errors["password"] = "password_required"
            else:
                try:
                    await self.async_set_unique_id(host.lower())
                    self._abort_if_unique_id_configured()
                except Exception as err:
                    _LOGGER.error("Error setting unique ID: %s", err)
                    errors["base"] = "unknown_error"
                else:
                    return self.async_create_entry(
                        title=f"Mennekes AMTRON - {host}",
                        data=user_input,
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Optional("api_port", default=80): int,
                    vol.Required("password"): str,
                    vol.Optional("modbus_port", default=502): int,
                    vol.Optional("electricity_price", default=0.29): vol.Coerce(
                        float
                    ),
                    vol.Optional("scan_interval", default=30): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=3600)
                    ),
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return MennekesOptionsFlow(config_entry)


class MennekesOptionsFlow(OptionsFlow):
    """Handle options for Mennekes AMTRON."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "electricity_price",
                        default=self.config_entry.data.get(
                            "electricity_price", 0.29
                        ),
                    ): vol.Coerce(float),
                    vol.Optional(
                        "scan_interval",
                        default=self.config_entry.data.get("scan_interval", 30),
                    ): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=3600)
                    ),
                }
            ),
        )
