from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN,
    CONF_WALLBOX_HOST,
    CONF_MODBUS_PORT,
    CONF_API_PASSWORD,
    CONF_PRICE_PER_KWH,
    CONF_SCAN_INTERVAL,
    DEFAULT_MODBUS_PORT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_PRICE_PER_KWH,
)

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_WALLBOX_HOST): str,
        vol.Optional(CONF_MODBUS_PORT, default=DEFAULT_MODBUS_PORT): int,
        vol.Required(CONF_API_PASSWORD): str,
        vol.Optional(CONF_PRICE_PER_KWH, default=DEFAULT_PRICE_PER_KWH): vol.Coerce(float),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class MennekesAmtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input[CONF_WALLBOX_HOST].strip()
            port = user_input[CONF_MODBUS_PORT]

            # Validate Modbus connection
            try:
                from pymodbus.client import AsyncModbusTcpClient
                client = AsyncModbusTcpClient(host, port=port)
                connected = await client.connect()
                client.close()
                if not connected:
                    errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(f"{host}:{port}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title=f"Mennekes AMTRON ({host})",
                    data={**user_input, CONF_WALLBOX_HOST: host},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return MennekesAmtronOptionsFlow(config_entry)


class MennekesAmtronOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry) -> None:
        self._entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_PRICE_PER_KWH,
                    default=self._entry.data.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
