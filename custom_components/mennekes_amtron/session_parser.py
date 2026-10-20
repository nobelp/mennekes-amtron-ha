"""Parsing of the wallbox charging transaction history.

Older firmware and firmware 1.6.46 return different field names and container
keys for the same data (see issue #10). The lookups below try the known names
in order, so both shapes work. This module has no Home Assistant imports and
can be tested on its own.
"""

from __future__ import annotations

from typing import Any

# Container keys that hold the session list, in order of preference.
_CONTAINER_KEYS = ("items", "data", "list")
# Field names per value, in order of preference. The first non-empty value wins.
_START_KEYS = ("startTime", "startTimestamp")
_END_KEYS = ("endTime", "stopTime", "stopTimestamp")
_ENERGY_KEYS = ("energyConsumption", "energy_kwh", "chargedEnergy")
_RFID_KEYS = ("rfidTag", "rfid")


def extract_sessions(body: Any) -> list[dict[str, Any]]:
    """Return the session list from a response body, whichever container it uses."""
    if isinstance(body, list):
        return body
    if not isinstance(body, dict):
        return []
    for key in _CONTAINER_KEYS:
        value = body.get(key)
        if isinstance(value, list):
            return value
    return []


def _first_value(raw: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first value that is set and not empty. A value of 0 counts as set."""
    for key in keys:
        value = raw.get(key)
        if value is not None and value != "":
            return value
    return None


def _rfid_of(raw: dict[str, Any]) -> str:
    rfid = _first_value(raw, _RFID_KEYS)
    if rfid is None:
        # Firmware 1.6.46 nests the tag; the value can be null.
        user_token = raw.get("userToken") or {}
        rfid = user_token.get("identifier") if isinstance(user_token, dict) else None
    return str(rfid or "")


def parse_session(raw: dict[str, Any]) -> dict[str, Any]:
    """Map one wallbox session to the fields the integration uses.

    Timestamps are kept as the wallbox sends them (ISO 8601 strings), so they
    can be sorted as text. Energy is in kWh.
    """
    return {
        "rfid": _rfid_of(raw),
        "energy_kwh": float(_first_value(raw, _ENERGY_KEYS) or 0),
        "start": str(_first_value(raw, _START_KEYS) or ""),
        "end": str(_first_value(raw, _END_KEYS) or ""),
    }


def parse_sessions(raw_sessions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Parse all sessions, newest first.

    The wallbox can return the oldest session first, so the order is set here
    and not taken from the response.
    """
    sessions = [parse_session(raw) for raw in raw_sessions]
    return sorted(sessions, key=lambda session: session["start"], reverse=True)
