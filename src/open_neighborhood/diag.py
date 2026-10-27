# Logging helpers: writes OpenNeighborhood_diag.txt next to the .ts4script file.
import os
import sys
import time
import traceback

LOG_NAME = "OpenNeighborhood_diag.txt"


def _mods_dir():
    # __file__ looks like ...\Mods\OpenNeighborhood.ts4script\open_neighborhood\diag.pyc
    path = os.path.abspath(__file__)
    probe = path
    for _ in range(8):
        parent = os.path.dirname(probe)
        if probe.lower().endswith(".ts4script"):
            return parent
        if parent == probe:
            break
        probe = parent
    return os.path.dirname(os.path.dirname(path))


def log_path():
    return os.path.join(_mods_dir(), LOG_NAME)


def log(*lines):
    try:
        with open(log_path(), "a", encoding="utf-8") as fh:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            for line in lines:
                fh.write("[{}] {}\n".format(stamp, line))
    except Exception:
        pass


def log_exception(where, exc):
    log("ERROR in {}: {!r}".format(where, exc), traceback.format_exc())


def on_import():
    log("=" * 60,
        "open_neighborhood imported",
        "python: {}".format(sys.version.replace("\n", " ")),
        "file: {}".format(os.path.abspath(__file__)))
