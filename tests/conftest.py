# Session setup and banner for the wic test suite.

import platform
import sys
from pathlib import Path

import pytest

_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

try:
    import wic.cli as _wic_cli
except Exception as exc:
    pytest.exit("cannot import wic from %s: %s" % (_SRC, exc), returncode=1)


def pytest_report_header(config):
    return "\n".join([
        "wic test suite",
        "  host:   %s  %s %s" % (
            platform.node(), platform.system(), platform.machine()),
        "  python: %s   pytest: %s" % (
            platform.python_version(), pytest.__version__),
        "  wic:    %s  (%s)" % (
            getattr(_wic_cli, "__version__", "(unknown)"), _wic_cli.__file__),
    ])
