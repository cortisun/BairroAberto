# Cheat-console commands. All are CommandType.Live so they work in the release
# build without testingcheats. (The default DebugOnly type is not available in the
# shipped game, which makes a command silently do nothing.)
import sys

import sims4.commands

from open_neighborhood import diag

LIVE = sims4.commands.CommandType.Live

# Native modules exported by Simulation_x64.dll (from the static PE export scan).
NATIVE_MODULES = (
    "_buildbuy", "_placement", "_pathing", "_terrain", "_zone", "_lot",
)

# Names that look relevant to lot/zone traversal. Only matched by name, never called.
KEYWORDS = ("zone", "lot", "waypoint", "polygon", "portal", "route", "street",
            "neighborhood", "travel", "footprint", "instanti", "load", "world")


def _out(_connection):
    return sims4.commands.CheatOutput(_connection)


def _safe(fn, default="?"):
    try:
        return fn()
    except Exception as exc:
        return "<{}: {}>".format(type(exc).__name__, exc)


@sims4.commands.Command("open_neighborhood.status", "on.status", command_type=LIVE)
def status(_connection=None):
    output = _out(_connection)
    try:
        import services
        from open_neighborhood import VERSION
        lines = [
            "Open Neighborhood {} loaded".format(VERSION),
            "python {}".format(sys.version.split()[0]),
            "current_zone_id: {}".format(_safe(services.current_zone_id)),
            "log: {}".format(diag.log_path()),
        ]
        for line in lines:
            output(line)
        diag.log("status:", *lines)
    except Exception as exc:
        output("status failed: {!r}".format(exc))
        diag.log_exception("status", exc)


def _describe_module(name):
    """Return (state, [(attr, kind)]) without calling anything in the module."""
    module = sys.modules.get(name)
    if module is None:
        return "not in sys.modules (not imported; left alone)", []
    entries = []
    for attr in sorted(dir(module)):
        if attr.startswith("__"):
            continue
        try:
            kind = type(getattr(module, attr)).__name__
        except Exception as exc:
            kind = "<getattr failed: {}>".format(type(exc).__name__)
        entries.append((attr, kind))
    return "loaded", entries


@sims4.commands.Command("open_neighborhood.native_api", "on.native_api", command_type=LIVE)
def native_api(filter_text: str = None, _connection=None):
    """Lists attribute names of the native modules. Full list goes to the log file."""
    output = _out(_connection)
    try:
        needle = filter_text.lower() if filter_text else None
        report = ["native_api dump (filter={})".format(filter_text)]
        for name in NATIVE_MODULES:
            state, entries = _describe_module(name)
            report.append("[{}] {} - {} names".format(name, state, len(entries)))
            hits = []
            for attr, kind in entries:
                low = attr.lower()
                if needle and needle not in low:
                    continue
                flag = "*" if any(k in low for k in KEYWORDS) else " "
                report.append("  {} {} ({})".format(flag, attr, kind))
                if flag == "*":
                    hits.append(attr)
            output("{}: {}, {} names, {} keyword hits".format(
                name, state.split(" ")[0], len(entries), len(hits)))
            if hits:
                output("   " + ", ".join(hits[:12]) + (" ..." if len(hits) > 12 else ""))
        diag.log(*report)
        output("full list written to {}".format(diag.log_path()))
    except Exception as exc:
        output("native_api failed: {!r}".format(exc))
        diag.log_exception("native_api", exc)


@sims4.commands.Command("open_neighborhood.zones", "on.zones", command_type=LIVE)
def zones(_connection=None):
    """Read-only look at which zones are instantiated and the current neighborhood's lots."""
    output = _out(_connection)
    try:
        import services
        report = []
        zone_manager = services.get_zone_manager()
        current = services.current_zone_id()
        ids = _safe(lambda: list(zone_manager.keys()), [])
        report.append("current_zone_id: {}".format(current))
        report.append("instantiated zones in ZoneManager: {} -> {}".format(
            len(ids) if isinstance(ids, list) else "?", ids))
        zone = services.current_zone()
        report.append("lot id: {}".format(_safe(lambda: zone.lot.lot_id)))
        report.append("neighborhood_id: {}".format(_safe(lambda: zone.neighborhood_id)))
        report.append("world_id: {}".format(_safe(lambda: zone.world_id)))

        persistence = services.get_persistence_service()
        hood = _safe(lambda: persistence.get_neighborhood_proto_buff(zone.neighborhood_id), None)
        lots = getattr(hood, "lots", None) if hood is not None and not isinstance(hood, str) else None
        if lots is not None:
            report.append("lots in this neighborhood: {}".format(len(lots)))
            for lot in lots:
                zid = _safe(lambda: lot.zone_instance_id)
                report.append("  zone {} | lot {} | instantiated={} | current={}".format(
                    zid, _safe(lambda: lot.lot_instance_id),
                    zid in ids if isinstance(ids, list) else "?", zid == current))
        else:
            report.append("neighborhood proto: {}".format(hood))
        for line in report[:8]:
            output(line)
        diag.log("zones:", *report)
        output("full list written to {}".format(diag.log_path()))
    except Exception as exc:
        output("zones failed: {!r}".format(exc))
        diag.log_exception("zones", exc)
