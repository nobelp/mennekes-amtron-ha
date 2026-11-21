"""The event list must not be written to the recorder database (issue #15).

The recorder drops all attributes of a state larger than 16384 bytes and logs a
warning on every update. The list is only read live by the dashboard, so the
large attributes are marked as unrecorded; they stay readable via state_attr().
"""

import pytest


@pytest.fixture
def sensor_class(integration):
    from importlib import import_module

    return import_module(f"{integration.__name__}.sensor").SystemEventsSensor


def test_large_attributes_are_not_recorded(sensor_class):
    assert {"events", "levels", "event_ids"} <= sensor_class._unrecorded_attributes


def test_small_attributes_stay_recorded(sensor_class):
    assert "fetched" not in sensor_class._unrecorded_attributes


def test_every_unrecorded_attribute_is_one_the_sensor_provides(sensor_class):
    class _Coordinator:
        data = {"events": [], "fetched": 0, "levels": [], "event_ids": [], "total": 0}

    sensor = sensor_class.__new__(sensor_class)
    sensor.coordinator = _Coordinator()

    provided = set(sensor.extra_state_attributes)

    assert sensor_class._unrecorded_attributes <= provided
