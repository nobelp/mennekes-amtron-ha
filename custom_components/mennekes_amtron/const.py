DOMAIN = "mennekes_amtron"
MANUFACTURER = "Mennekes"
# Fallback only — the actual model comes from the wallbox via /api/v1/PublicInfo.
# The 4You 400/500 and 4Business 600/700 series share one Modbus register set.
MODEL = "AMTRON 4You / 4Business"

CONF_WALLBOX_HOST = "host"
CONF_MODBUS_PORT = "modbus_port"
CONF_API_PORT = "api_port"
CONF_API_PASSWORD = "api_password"
CONF_PRICE_PER_KWH = "price_per_kwh"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_VEHICLES = "vehicles"  # options key: {rfid: vehicle name}

DEFAULT_MODBUS_PORT = 502
DEFAULT_API_PORT = 80
DEFAULT_SCAN_INTERVAL = 30
DEFAULT_PRICE_PER_KWH = 0.29
DEFAULT_API_TIMEOUT = 10  # seconds
MODBUS_CONNECT_TIMEOUT = 5  # seconds

# REST API
API_EVENT_LIMIT = 300  # events fetched per call; the wallbox pages at 100 by default
API_SESSION_LIMIT = 100
EVENT_LEVELS = ("All", "Information", "Error")
FILTER_ALL = "All"

MODBUS_SLAVE_ID = 1

# Modbus register addresses (Protocol v1.5)
REG_CP_STATUS = 104
REG_ERROR_CODE_1 = 105
REG_VEHICLE_STATE = 122
REG_CP_AVAILABILITY = 124
REG_SAFE_CURRENT = 131
REG_COMM_TIMEOUT = 132
REG_OPERATOR_CURRENT_LIMIT = 134

# Meter registers 200-227. Every meter value is an int32 spanning two
# registers, so consecutive phases are 2 apart (Modbus doc v1.5, page 2).
REG_ENERGY_L1 = 200
REG_ENERGY_L2 = 202
REG_ENERGY_L3 = 204
REG_POWER_L1 = 206
REG_POWER_L2 = 208
REG_POWER_L3 = 210
REG_CURRENT_L1 = 212  # mA
REG_CURRENT_L2 = 214
REG_CURRENT_L3 = 216
REG_TOTAL_ENERGY = 218
REG_TOTAL_POWER = 220
REG_VOLTAGE_L1 = 222
REG_VOLTAGE_L2 = 224
REG_VOLTAGE_L3 = 226
METER_BLOCK_COUNT = 28  # 200-227

# Charging session registers
REG_SIGNALED_CURRENT = 706
REG_MIN_CURRENT_LIMIT = 712
REG_MAX_CURRENT_EV = 715
REG_SESSION_ENERGY = 716
REG_SESSION_DURATION = 718

# Phase switch registers (v1.5)
REG_PHASE_SWITCH_MODE = 2020
REG_PHASE_SWITCH_PAUSE = 2021
REG_PHASE_SWITCH_STATUS = 2022
REG_ASSIGNED_PHASES = 2023

# HEMS registers (v1.5 - replaces deprecated 1000-1002)
REG_HEMS_CURRENT_LIMIT = 2000
REG_HEMS_CURRENT_LIMIT_01A = 2001
REG_HEMS_POWER_LIMIT = 2002
REG_HEMS_CONFIG = 2010
REG_HEMS_COMM_STATUS = 2011
REG_HEMS_POWER_MIN = 2012
REG_HEMS_POWER_MAX = 2013
REG_AUTHORIZATION_STATUS = 2030

CP_STATUS_MAP = {
    0: "Unknown",
    1: "Available",
    2: "Preparing",
    3: "Charging",
    4: "SuspendedEVSE",
    5: "SuspendedEV",
    6: "Finishing",
    7: "Reserved",
    8: "Unavailable",
    9: "Faulted",
}

VEHICLE_STATE_MAP = {
    1: "A – Not connected",
    2: "B – Connected",
    3: "C – Charging",
    4: "D – Charging (ventilation)",
    5: "E – Error",
}
