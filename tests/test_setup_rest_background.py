"""A slow REST API of the wallbox must not delay or abort the setup.

Before 2.3.4-beta.2 the entry setup awaited the first REST refresh. When the
wallbox web service did not finish its response, the setup hung for up to 90 s
and, once cancelled, left every entity unavailable although Modbus worked.
"""

import asyncio

import pytest
from ha_stubs import UpdateFailed


class _FakeCoordinator:
    """Replaces the real coordinators; records refreshes and can hang forever."""

    refresh_log: list[str] = []

    def __init__(self, name: str, hangs: bool = False, fails: bool = False) -> None:
        self.name = name
        self._hangs = hangs
        self._fails = fails

    async def async_config_entry_first_refresh(self) -> None:
        if self._hangs:
            await asyncio.Event().wait()
        if self._fails:
            raise UpdateFailed("wallbox did not answer")

    async def async_refresh(self) -> None:
        _FakeCoordinator.refresh_log.append(self.name)
        if self._hangs:
            await asyncio.Event().wait()

    def set_vehicles(self, vehicles) -> None:
        pass


class _FakeEntry:
    entry_id = "entry-1"
    data = {"host": "192.0.2.10", "api_password": "example"}
    options: dict = {}

    def __init__(self) -> None:
        self.background_tasks: list = []

    def async_on_unload(self, _callback) -> None:
        pass

    def add_update_listener(self, _listener):
        return lambda: None

    def async_create_background_task(self, hass, target, name):
        self.background_tasks.append((name, target))


class _FakeBus:
    def async_listen(self, _event, _callback):
        return lambda: None


class _FakeConfigEntries:
    async def async_forward_entry_setups(self, _entry, _platforms) -> None:
        return None


class _FakeHass:
    def __init__(self) -> None:
        self.data: dict = {}
        self.bus = _FakeBus()
        self.config_entries = _FakeConfigEntries()


@pytest.fixture
def setup(integration, monkeypatch):
    _FakeCoordinator.refresh_log = []

    async def no_public_info(*_args, **_kwargs):
        return {}

    monkeypatch.setattr(integration, "_fetch_public_info", no_public_info)

    def install(modbus_fails: bool = False, rest_hangs: bool = False):
        monkeypatch.setattr(
            integration, "ModbusDataCoordinator",
            lambda *_a, **_k: _FakeCoordinator("modbus", fails=modbus_fails),
        )
        monkeypatch.setattr(
            integration, "SessionDataCoordinator",
            lambda *_a, **_k: _FakeCoordinator("sessions", hangs=rest_hangs),
        )
        monkeypatch.setattr(
            integration, "SystemEventsCoordinator",
            lambda *_a, **_k: _FakeCoordinator("events", hangs=rest_hangs),
        )
        return integration

    return install


def test_setup_finishes_although_the_rest_api_hangs(setup):
    integration = setup(rest_hangs=True)
    entry = _FakeEntry()

    result = asyncio.run(
        asyncio.wait_for(integration.async_setup_entry(_FakeHass(), entry), timeout=1)
    )

    assert result is True
    assert _FakeCoordinator.refresh_log == []  # nothing waited for the REST API
    for _name, task in entry.background_tasks:
        task.close()  # never started here; avoids a "never awaited" warning


def test_rest_data_is_loaded_in_a_background_task_of_the_entry(setup):
    integration = setup()
    entry = _FakeEntry()
    asyncio.run(integration.async_setup_entry(_FakeHass(), entry))

    assert len(entry.background_tasks) == 1
    name, task = entry.background_tasks[0]
    assert name == "mennekes_amtron_initial_rest_refresh"

    asyncio.run(task)

    assert _FakeCoordinator.refresh_log == ["sessions", "events"]


def test_setup_fails_when_the_modbus_data_cannot_be_read(setup):
    integration = setup(modbus_fails=True)
    entry = _FakeEntry()

    with pytest.raises(UpdateFailed):
        asyncio.run(integration.async_setup_entry(_FakeHass(), entry))

    assert entry.background_tasks == []
