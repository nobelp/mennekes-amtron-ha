"""Regression tests for issue #10: firmware 1.6.46 session history.

All data is synthetic. RFID tags are made-up values.
"""

import session_parser as sp


# Older firmware: container "items", camel-case names with "time" suffix.
LEGACY_SESSION = {
    "rfidTag": "RFID-A",
    "energyConsumption": 12.5,
    "startTime": "2026-05-01T08:00:00Z",
    "endTime": "2026-05-01T18:00:00Z",
}

# Firmware 1.6.46: container "list", "...Timestamp" names, nested user token.
FIRMWARE_1_6_46_SESSION = {
    "chargedEnergy": 7.25,
    "startTimestamp": "2026-10-10T09:31:50Z",
    "stopTimestamp": "2026-10-11T17:14:28Z",
    "userToken": {"identifier": "RFID-B"},
}


class TestExtractSessions:
    def test_reads_plain_list(self):
        assert sp.extract_sessions([LEGACY_SESSION]) == [LEGACY_SESSION]

    def test_reads_items_container(self):
        assert sp.extract_sessions({"items": [LEGACY_SESSION]}) == [LEGACY_SESSION]

    def test_reads_data_container(self):
        assert sp.extract_sessions({"data": [LEGACY_SESSION]}) == [LEGACY_SESSION]

    def test_reads_list_container_of_1_6_46(self):
        body = {"list": [FIRMWARE_1_6_46_SESSION], "count": 1}
        assert sp.extract_sessions(body) == [FIRMWARE_1_6_46_SESSION]

    def test_returns_empty_list_for_unknown_shape(self):
        assert sp.extract_sessions({"count": 3}) == []
        assert sp.extract_sessions(None) == []
        assert sp.extract_sessions("unexpected") == []


class TestParseSession:
    def test_legacy_field_names(self):
        parsed = sp.parse_session(LEGACY_SESSION)
        assert parsed == {
            "rfid": "RFID-A",
            "energy_kwh": 12.5,
            "start": "2026-05-01T08:00:00Z",
            "end": "2026-05-01T18:00:00Z",
        }

    def test_firmware_1_6_46_field_names(self):
        parsed = sp.parse_session(FIRMWARE_1_6_46_SESSION)
        assert parsed == {
            "rfid": "RFID-B",
            "energy_kwh": 7.25,
            "start": "2026-10-10T09:31:50Z",
            "end": "2026-10-11T17:14:28Z",
        }

    def test_zero_energy_is_kept_and_not_replaced_by_fallback(self):
        raw = {"energyConsumption": 0, "chargedEnergy": 5.0}
        assert sp.parse_session(raw)["energy_kwh"] == 0.0

    def test_null_user_token_gives_empty_rfid(self):
        raw = {"chargedEnergy": 1.0, "userToken": None}
        assert sp.parse_session(raw)["rfid"] == ""

    def test_missing_fields_give_neutral_values(self):
        parsed = sp.parse_session({})
        assert parsed == {"rfid": "", "energy_kwh": 0.0, "start": "", "end": ""}

    def test_rfid_field_is_used_when_tag_is_absent(self):
        assert sp.parse_session({"rfid": "RFID-C"})["rfid"] == "RFID-C"


class TestParseSessions:
    def test_orders_oldest_first_input_newest_first(self):
        # Firmware 1.6.46 returns the oldest session first.
        raw = [
            {"startTimestamp": "2026-10-01T08:00:00Z", "chargedEnergy": 1.0},
            {"startTimestamp": "2026-10-10T09:31:50Z", "chargedEnergy": 2.0},
            {"startTimestamp": "2026-10-05T07:00:00Z", "chargedEnergy": 3.0},
        ]
        starts = [s["start"] for s in sp.parse_sessions(raw)]
        assert starts == [
            "2026-10-10T09:31:50Z",
            "2026-10-05T07:00:00Z",
            "2026-10-01T08:00:00Z",
        ]

    def test_newest_session_is_first_for_mixed_formats(self):
        raw = [LEGACY_SESSION, FIRMWARE_1_6_46_SESSION]
        parsed = sp.parse_sessions(raw)
        assert parsed[0]["rfid"] == "RFID-B"

    def test_empty_input_gives_empty_list(self):
        assert sp.parse_sessions([]) == []
