"""Load session_parser without importing the integration package.

The package __init__ imports Home Assistant, which is not needed to test the
pure parsing functions. The module is loaded from its file path instead.
"""

import importlib.util
import sys
from pathlib import Path

_MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "mennekes_amtron"
    / "session_parser.py"
)

_spec = importlib.util.spec_from_file_location("session_parser", _MODULE_PATH)
session_parser = importlib.util.module_from_spec(_spec)
sys.modules["session_parser"] = session_parser
_spec.loader.exec_module(session_parser)
