"""Minimal stand-ins for Home Assistant, aiohttp and pymodbus.

The integration is loaded from its source directory, so the tests need neither
Home Assistant nor pymodbus. Only the names the integration imports exist.
"""

import enum
import importlib.util
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Any

COMPONENT_DIR = Path(__file__).resolve().parent.parent / "custom_components" / "mennekes_amtron"
PACKAGE_NAME = "amtron_under_test"


class UpdateFailed(Exception):
    """Stand-in for homeassistant.helpers.update_coordinator.UpdateFailed."""


class ConfigEntryAuthFailed(Exception):
    """Stand-in for homeassistant.exceptions.ConfigEntryAuthFailed."""


class DataUpdateCoordinator:
    """Stand-in that accepts the constructor arguments of the real class."""

    def __init__(self, hass, logger, *, name, update_interval=None):
        self.hass = hass
        self.name = name


class CoordinatorEntity:
    """Stand-in base class; subscripting (CoordinatorEntity[...]) is allowed."""

    def __class_getitem__(cls, _item):
        return cls


class Platform(enum.Enum):
    SENSOR = "sensor"
    NUMBER = "number"
    SWITCH = "switch"
    SELECT = "select"
    TEXT = "text"
    BUTTON = "button"


class FakeModbusClient:
    """Records how it is created and closed; the connection result is configurable."""

    instances: list["FakeModbusClient"] = []
    connects_successfully = True

    def __init__(self, host, port, **kwargs):
        self.kwargs = kwargs
        self.connected = False
        self.close_calls = 0
        FakeModbusClient.instances.append(self)

    async def connect(self):
        self.connected = FakeModbusClient.connects_successfully
        return self.connected

    def close(self):
        self.close_calls += 1
        self.connected = False


class _AnyMember(type):
    """Metaclass: every attribute access yields a member, like an enum would."""

    def __getattr__(cls, name):
        return f"{cls.__name__}.{name}"


class _EnumLike(metaclass=_AnyMember):
    pass


def _enum_like(name: str) -> type:
    return _AnyMember(name, (_EnumLike,), {})


@dataclass(frozen=True, kw_only=True)
class SensorEntityDescription:
    """Stand-in with the fields the integration's sensor descriptions set."""

    key: str
    name: Any = None
    native_unit_of_measurement: Any = None
    device_class: Any = None
    state_class: Any = None
    options: Any = None
    translation_key: Any = None
    icon: Any = None
    suggested_display_precision: Any = None
    entity_category: Any = None


class SensorEntity:
    """Stand-in base class of the sensor entities."""

    # Home Assistant's Entity declares the same default.
    _unrecorded_attributes: frozenset[str] = frozenset()


def _module(name: str, **attributes) -> types.ModuleType:
    module = types.ModuleType(name)
    vars(module).update(attributes)
    return module


def load_integration(monkeypatch) -> types.ModuleType:
    """Import the integration package with the stand-ins and return it."""
    FakeModbusClient.instances = []
    FakeModbusClient.connects_successfully = True

    stand_ins = {
        "aiohttp": _module("aiohttp", ClientSession=object, ClientTimeout=lambda **_: None),
        "homeassistant": _module("homeassistant"),
        "homeassistant.config_entries": _module(
            "homeassistant.config_entries", ConfigEntry=object
        ),
        "homeassistant.const": _module(
            "homeassistant.const",
            EVENT_CORE_CONFIG_UPDATE="core_config_updated",
            Platform=Platform,
            UnitOfElectricCurrent=_enum_like("UnitOfElectricCurrent"),
            UnitOfElectricPotential=_enum_like("UnitOfElectricPotential"),
            UnitOfEnergy=_enum_like("UnitOfEnergy"),
            UnitOfPower=_enum_like("UnitOfPower"),
            UnitOfTime=_enum_like("UnitOfTime"),
        ),
        "homeassistant.core": _module(
            "homeassistant.core",
            Event=object,
            HomeAssistant=object,
            callback=lambda function: function,
        ),
        "homeassistant.exceptions": _module(
            "homeassistant.exceptions", ConfigEntryAuthFailed=ConfigEntryAuthFailed
        ),
        "homeassistant.helpers": _module("homeassistant.helpers"),
        "homeassistant.helpers.update_coordinator": _module(
            "homeassistant.helpers.update_coordinator",
            DataUpdateCoordinator=DataUpdateCoordinator,
            CoordinatorEntity=CoordinatorEntity,
            UpdateFailed=UpdateFailed,
        ),
        "homeassistant.components": _module("homeassistant.components"),
        "homeassistant.components.sensor": _module(
            "homeassistant.components.sensor",
            SensorDeviceClass=_enum_like("SensorDeviceClass"),
            SensorEntity=SensorEntity,
            SensorEntityDescription=SensorEntityDescription,
            SensorStateClass=_enum_like("SensorStateClass"),
        ),
        "homeassistant.helpers.entity": _module(
            "homeassistant.helpers.entity", DeviceInfo=dict
        ),
        "homeassistant.helpers.entity_platform": _module(
            "homeassistant.helpers.entity_platform", AddEntitiesCallback=object
        ),
        "pymodbus": _module("pymodbus"),
        "pymodbus.client": _module("pymodbus.client", AsyncModbusTcpClient=FakeModbusClient),
    }
    for name, module in stand_ins.items():
        monkeypatch.setitem(sys.modules, name, module)

    spec = importlib.util.spec_from_file_location(
        PACKAGE_NAME,
        COMPONENT_DIR / "__init__.py",
        submodule_search_locations=[str(COMPONENT_DIR)],
    )
    package = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, PACKAGE_NAME, package)
    spec.loader.exec_module(package)
    return package


def unload_integration() -> None:
    """Forget the imported package so that every test starts from a clean import."""
    for name in [n for n in sys.modules if n == PACKAGE_NAME or n.startswith(f"{PACKAGE_NAME}.")]:
        del sys.modules[name]
