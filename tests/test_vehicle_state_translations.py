"""Every vehicle state must be translated in all language files."""

import importlib.util
import json
from pathlib import Path

_COMPONENT = Path(__file__).resolve().parent.parent / "custom_components" / "mennekes_amtron"

_spec = importlib.util.spec_from_file_location("amtron_const", _COMPONENT / "const.py")
_const = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_const)

LANGUAGE_FILES = ("strings.json", "translations/de.json", "translations/en.json")


def _translated_states(filename: str) -> dict[str, str]:
    data = json.loads((_COMPONENT / filename).read_text(encoding="utf-8"))
    return data["entity"]["sensor"]["vehicle_state"]["state"]


def test_all_states_are_translated_in_every_language_file():
    expected = set(_const.VEHICLE_STATE_MAP.values())
    for filename in LANGUAGE_FILES:
        assert set(_translated_states(filename)) == expected, filename


def test_german_translation_differs_from_english():
    german = _translated_states("translations/de.json")
    english = _translated_states("translations/en.json")
    assert all(german[key] != english[key] for key in english)
