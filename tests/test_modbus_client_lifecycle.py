"""The Modbus coordinator must never leave an abandoned client behind (issue #13).

The wallbox serves one Modbus client at a time. A client that is replaced
without close() keeps reconnecting in the background (pymodbus auto-reconnect)
and piles up sessions until the wallbox stops answering.

Home Assistant and pymodbus are replaced by minimal stand-ins, so the tests
need neither package. The coordinator is loaded from its file path.
"""

import asyncio
import importlib.util
import sys
import types
from pathlib import Path

import pytest

_COMPONENT = Path(__file__).resolve().parent.parent / "custom_components" / "mennekes_amtron"


class _UpdateFailed(Exception):
    """Stand-in for homeassistant.helpers.update_coordinator.UpdateFailed."""


class _DataUpdateCoordinator:
    """Stand-in that accepts the constructor arguments of the real class."""

    def __init__(self, hass, logger, *, name, update_interval=None):
        self.hass = hass


class _FakeModbusClient:
    """Records how it is created and closed; connection result is configurable."""

    instances: list["_FakeModbusClient"] = []
    connects_successfully = True

    def __init__(self, host, port, **kwargs):
        self.kwargs = kwargs
        self.connected = False
        self.close_calls = 0
        _FakeModbusClient.instances.append(self)

    async def connect(self):
        self.connected = _FakeModbusClient.connects_successfully
        return self.connected

    def close(self):
        self.close_calls += 1
        self.connected = False


def _module(name: str, **attributes) -> types.ModuleType:
    module = types.ModuleType(name)
    vars(module).update(attributes)
    return module


@pytest.fixture
def coordinator_module(monkeypatch):
    _FakeModbusClient.instances = []
    _FakeModbusClient.connects_successfully = True

    stand_ins = {
        "aiohttp": _module("aiohttp", ClientSession=object),
        "homeassistant": _module("homeassistant"),
        "homeassistant.core": _module("homeassistant.core", HomeAssistant=object),
        "homeassistant.exceptions": _module(
            "homeassistant.exceptions", ConfigEntryAuthFailed=Exception
        ),
        "homeassistant.helpers": _module("homeassistant.helpers"),
        "homeassistant.helpers.update_coordinator": _module(
            "homeassistant.helpers.update_coordinator",
            DataUpdateCoordinator=_DataUpdateCoordinator,
            UpdateFailed=_UpdateFailed,
        ),
        "pymodbus": _module("pymodbus"),
        "pymodbus.client": _module("pymodbus.client", AsyncModbusTcpClient=_FakeModbusClient),
    }
    for name, module in stand_ins.items():
        monkeypatch.setitem(sys.modules, name, module)

    # A bare package object avoids running the integration's __init__, which
    # imports the full Home Assistant platform.
    package = types.ModuleType("amtron_under_test")
    package.__path__ = [str(_COMPONENT)]
    monkeypatch.setitem(sys.modules, "amtron_under_test", package)

    spec = importlib.util.spec_from_file_location(
        "amtron_under_test.coordinator", _COMPONENT / "coordinator.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, "amtron_under_test.coordinator", module)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def coordinator(coordinator_module):
    return coordinator_module.ModbusDataCoordinator(None, "192.0.2.10", 502, 30)


def test_new_client_disables_pymodbus_auto_reconnect(coordinator):
    asyncio.run(coordinator._get_client())

    assert _FakeModbusClient.instances[0].kwargs["reconnect_delay"] == 0


def test_connected_client_is_reused(coordinator):
    first = asyncio.run(coordinator._get_client())
    second = asyncio.run(coordinator._get_client())

    assert first is second
    assert len(_FakeModbusClient.instances) == 1


def test_stale_client_is_closed_before_it_is_replaced(coordinator):
    stale = asyncio.run(coordinator._get_client())
    stale.connected = False  # the wallbox dropped the session

    replacement = asyncio.run(coordinator._get_client())

    assert replacement is not stale
    assert stale.close_calls == 1


def test_client_is_closed_when_connect_does_not_stay_connected(coordinator_module, coordinator):
    _FakeModbusClient.connects_successfully = False

    with pytest.raises(_UpdateFailed):
        asyncio.run(coordinator._get_client())

    failed = _FakeModbusClient.instances[0]
    assert failed.close_calls == 1
    assert coordinator._client is None


def test_repeated_failures_hold_no_open_clients(coordinator):
    _FakeModbusClient.connects_successfully = False

    for _ in range(5):
        with pytest.raises(_UpdateFailed):
            asyncio.run(coordinator._get_client())

    assert len(_FakeModbusClient.instances) == 5
    assert all(client.close_calls == 1 for client in _FakeModbusClient.instances)


def test_async_close_closes_current_client(coordinator):
    client = asyncio.run(coordinator._get_client())

    asyncio.run(coordinator.async_close())

    assert client.close_calls == 1
    assert coordinator._client is None


def test_async_close_without_client_does_nothing(coordinator):
    asyncio.run(coordinator.async_close())

    assert coordinator._client is None
