"""Config flow for Mennekes AMTRON integration."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
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
    DEFAULT_API_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)


class InvalidCredentials(Exception):
    """The wallbox rejected the supplied credentials."""


STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_WALLBOX_HOST): str,
        vol.Optional(CONF_API_PORT, default=DEFAULT_API_PORT): int,
        vol.Optional(CONF_MODBUS_PORT, default=DEFAULT_MODBUS_PORT): int,
        vol.Required(CONF_API_PASSWORD): str,
        vol.Optional(CONF_PRICE_PER_KWH, default=DEFAULT_PRICE_PER_KWH): vol.Coerce(float),
        vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL): int,
    }
)


class MennekesAmtronConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for Mennekes AMTRON integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Normalize and validate host
            host = user_input[CONF_WALLBOX_HOST].strip().lower()
            api_port = user_input[CONF_API_PORT]
            modbus_port = user_input[CONF_MODBUS_PORT]

            if not host:
                errors[CONF_WALLBOX_HOST] = "invalid_host"
            elif api_port <= 0 or api_port > 65535:
                errors[CONF_API_PORT] = "invalid_port"
            elif modbus_port <= 0 or modbus_port > 65535:
                errors[CONF_MODBUS_PORT] = "invalid_port"
            else:
                # Validate connection to wallbox via API
                try:
                    validation_result = await self._validate_wallbox(
                        host, api_port, user_input[CONF_API_PASSWORD]
                    )
                    if not validation_result:
                        errors["base"] = "cannot_connect"
                except asyncio.TimeoutError:
                    _LOGGER.warning(
                        "Timeout connecting to wallbox at %s:%d", host, api_port
                    )
                    errors["base"] = "timeout_connect"
                except aiohttp.ClientSSLError:
                    _LOGGER.error("SSL error connecting to wallbox")
                    errors["base"] = "ssl_error"
                except aiohttp.ClientConnectorError:
                    _LOGGER.warning("Connection error to wallbox at %s:%d", host, api_port)
                    errors["base"] = "cannot_connect"
                except InvalidCredentials:
                    _LOGGER.warning("Invalid credentials for wallbox")
                    errors["base"] = "invalid_credentials"
                except Exception:
                    _LOGGER.exception("Unexpected error validating wallbox connection")
                    errors["base"] = "unknown_error"

            if not errors:
                # Set unique ID to prevent duplicates
                unique_id = f"{host}:{modbus_port}"
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Mennekes AMTRON ({host})",
                    data={
                        **user_input,
                        CONF_WALLBOX_HOST: host,
                        CONF_API_PORT: api_port,
                        CONF_MODBUS_PORT: modbus_port,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_SCHEMA,
            errors=errors,
        )

    async def _validate_wallbox(
        self, host: str, port: int, password: str
    ) -> bool:
        """Validate connection to wallbox by fetching public info."""
        timeout = aiohttp.ClientTimeout(total=DEFAULT_API_TIMEOUT)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f"http://{host}:{port}/api/v1/PublicInfo"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Check that we got valid response with expected fields
                        if isinstance(data, dict):
                            _LOGGER.debug(
                                "Successfully validated wallbox at %s:%d", host, port
                            )
                            return True
                    elif response.status in (401, 403):
                        raise InvalidCredentials(
                            f"Wallbox rejected the request with HTTP {response.status}"
                        )
                    else:
                        _LOGGER.warning(
                            "Wallbox returned status %d for %s:%d",
                            response.status,
                            host,
                            port,
                        )
                        return False
        except asyncio.TimeoutError:
            _LOGGER.warning(
                "Timeout connecting to wallbox at %s:%d after %d seconds",
                host,
                port,
                DEFAULT_API_TIMEOUT,
            )
            raise
        except aiohttp.ClientSSLError as err:
            _LOGGER.error("SSL error connecting to %s:%d: %s", host, port, err)
            raise
        except aiohttp.ClientConnectorError as err:
            _LOGGER.warning("Connection error to %s:%d: %s", host, port, err)
            raise
        except InvalidCredentials as err:
            _LOGGER.warning("Authentication error for %s:%d: %s", host, port, err)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP error connecting to %s:%d: %s", host, port, err)
            raise
        except ValueError as err:
            _LOGGER.error("Invalid JSON response from %s:%d: %s", host, port, err)
            return False

        return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        """Return the options flow."""
        return MennekesAmtronOptionsFlow(config_entry)


class MennekesAmtronOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Mennekes AMTRON integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial options step."""
        if user_input is not None:
            # Preserve the RFID → vehicle mapping; it lives in the same options dict
            # and would be dropped by replacing options wholesale.
            return self.async_create_entry(
                title="",
                data={
                    **self._entry.options,
                    **user_input,
                },
            )

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_PRICE_PER_KWH,
                    default=self._entry.data.get(CONF_PRICE_PER_KWH, DEFAULT_PRICE_PER_KWH),
                ): vol.Coerce(float),
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self._entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=3600)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
