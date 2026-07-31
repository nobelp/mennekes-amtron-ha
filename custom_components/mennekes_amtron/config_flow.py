"""Config flow for Mennekes AMTRON Wallbox integration."""

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import CONF_API_PORT, DEFAULT_API_PORT, DEFAULT_API_TIMEOUT, DOMAIN

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
            try:
                await self.async_step_validate_input(user_input)
                await self.async_set_unique_id(
                    user_input.get("host", "").lower()
                )
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Mennekes AMTRON ({user_input.get('host')})",
                    data=user_input,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except asyncio.TimeoutError:
                errors["base"] = "timeout"
            except Exception as exc:
                _LOGGER.exception("Unexpected error during validation: %s", exc)
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host"): str,
                    vol.Optional(CONF_API_PORT, default=DEFAULT_API_PORT): int,
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
            description_placeholders={
                "wallbox_ip": "e.g., 192.168.2.179 or wallbox.local"
            },
        )

    @staticmethod
    async def async_step_validate_input(user_input: Dict[str, Any]) -> None:
        """Validate the user input allows us to connect."""
        host = user_input.get("host", "").strip()
        port = user_input.get(CONF_API_PORT, DEFAULT_API_PORT)
        password = user_input.get("password", "")

        if not host:
            raise vol.Invalid("host is required")

        if not isinstance(port, int) or port < 1 or port > 65535:
            raise vol.Invalid("port must be between 1 and 65535")

        if not password:
            raise vol.Invalid("password is required")

        try:
            session = aiohttp_client.async_get_clientsession(None)
            url = f"http://{host}:{port}/api/v1/PublicInfo"

            async with session.get(url, timeout=aiohttp.ClientTimeout(total=DEFAULT_API_TIMEOUT)) as response:
                if response.status == 401 or response.status == 403:
                    raise InvalidAuth()
                if response.status != 200:
                    raise CannotConnect(
                        f"HTTP {response.status}: {response.reason}"
                    )

                data = await response.json()
                if not data:
                    raise CannotConnect("Empty response from wallbox")

        except asyncio.TimeoutError as exc:
            raise asyncio.TimeoutError("Connection timeout to wallbox") from exc
        except aiohttp.ClientConnectorError as exc:
            raise CannotConnect(f"Connection error: {exc}") from exc
        except aiohttp.ClientSSLError as exc:
            raise CannotConnect(f"SSL/TLS error: {exc}") from exc
        except aiohttp.ClientConnectorError as exc:
            raise CannotConnect(f"Connection error: {exc}") from exc
        except aiohttp.ClientError as exc:
            raise CannotConnect(f"Network error: {exc}") from exc

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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication."""
