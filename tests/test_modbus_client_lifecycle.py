"""The Modbus coordinator must never leave an abandoned client behind (issue #13).

The wallbox serves one Modbus client at a time. A client that is replaced
without close() keeps reconnecting in the background (pymodbus auto-reconnect)
and piles up sessions until the wallbox stops answering.

Home Assistant and pymodbus are replaced by the stand-ins of ha_stubs, so the
tests need neither package.
"""

import asyncio

import pytest
from ha_stubs import FakeModbusClient as _FakeModbusClient
from ha_stubs import UpdateFailed as _UpdateFailed


@pytest.fixture
def coordinator_module(integration):
    return integration.coordinator


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
