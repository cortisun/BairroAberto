# Cheat-console commands. All are CommandType.Live so they work in the release
# build without testingcheats. (The default DebugOnly type is not available in the
# shipped game, which makes a command silently do nothing.)
import sys

import sims4.commands

from open_neighborhood import diag, probe, introspection, neighbor_preview

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


@sims4.commands.Command("open_neighborhood.neighbors", "on.neighbors", command_type=LIVE)
def neighbors(_connection=None):
    """Report which neighboring lot records exist without loading them."""
    output = _out(_connection)
    try:
        import services
        report = probe.overview(services)
        diag.log("neighbors:", *report)
        for line in report[:12]:
            output(line)
        output("relatorio completo: {}".format(diag.log_path()))
    except Exception as exc:
        output("neighbors failed: {!r}".format(exc))
        diag.log_exception("neighbors", exc)


@sims4.commands.Command("open_neighborhood.inspect", "on.inspect", command_type=LIVE)
def inspect_zone(target_zone_id: int = 0, _connection=None):
    """Inspect a neighbor by its zone id, without loading or changing it."""
    output = _out(_connection)
    if target_zone_id <= 0:
        output("Uso: on.inspect <ID_da_zona> (veja on.neighbors)")
        return
    try:
        import services
        report = probe.inspect_neighbor(services, target_zone_id)
        diag.log("inspect:", *report)
        for line in report[:10]:
            output(line)
        output("relatorio completo: {}".format(diag.log_path()))
    except Exception as exc:
        output("inspect failed: {!r}".format(exc))
        diag.log_exception("inspect", exc)


@sims4.commands.Command("open_neighborhood.native_info", "on.native_info", command_type=LIVE)
def native_info(module_name: str = "_buildbuy", symbol_name: str = "get_zones_cached_objects", _connection=None):
    """Report signatures and docs; DOES NOT execute any native function."""
    output = _out(_connection)
    try:
        report = introspection.native_info(sys.modules, module_name, symbol_name)
        diag.log("native_info:", *report)
        for line in report:
            output(line)
        output("relatorio: {}".format(diag.log_path()))
    except Exception as exc:
        output("native_info failed: {!r}".format(exc))
        diag.log_exception("native_info", exc)


@sims4.commands.Command("open_neighborhood.class_api", "on.class_api", command_type=LIVE)
def class_api(_connection=None):
    """List relevant descriptors on the loaded zone/lot classes, without calling them."""
    output = _out(_connection)
    try:
        import services
        report = introspection.class_info(services.current_zone())
        diag.log("class_api:", *report)
        for line in report[:12]:
            output(line)
        output("relatorio completo: {}".format(diag.log_path()))
    except Exception as exc:
        output("class_api failed: {!r}".format(exc))
        diag.log_exception("class_api", exc)


@sims4.commands.Command("open_neighborhood.capture_neighbor", "on.capture_neighbor", command_type=LIVE)
def capture_neighbor(_connection=None):
    """When physically visiting a neighbor, record its movable object definitions."""
    output = _out(_connection)
    try:
        import services
        data = neighbor_preview.capture(services)
        destination = neighbor_preview.save_capture(data)
        output("Capturados {} objetos da zona {}.".format(
            len(data["objects"]), data["source_zone_id"]))
        output("Agora volte normalmente para sua casa e use on.captured.")
        diag.log("capture_neighbor:", "count={}".format(len(data["objects"])),
                 "source_zone_id={}".format(data["source_zone_id"]),
                 "file={}".format(destination))
    except Exception as exc:
        output("capture_neighbor falhou: {!r}".format(exc))
        diag.log_exception("capture_neighbor", exc)


@sims4.commands.Command("open_neighborhood.captured", "on.captured", command_type=LIVE)
def captured(_connection=None):
    """List recorded furniture to select the index for a single preview."""
    output = _out(_connection)
    try:
        data = neighbor_preview.load_capture()
        output("Zona capturada: {} | objetos: {}".format(
            data["source_zone_id"], len(data["objects"])))
        report = []
        for index, item in enumerate(data["objects"]):
            line = "  {}: definition={} pos={} {}".format(
                index, item["definition_id"], item["position"], item["label"])
            report.append(line)
        for line in report[:12]:
            output(line)
        diag.log("captured:", *report)
        output("Lista completa no OpenNeighborhood_diag.txt")
    except Exception as exc:
        output("captured falhou: {!r}".format(exc))
        diag.log_exception("captured", exc)


@sims4.commands.Command("open_neighborhood.preview_one", "on.preview_one", command_type=LIVE)
def preview_one(index: int = 0, _connection=None):
    """Explicitly test spawning ONE neighbor object at its off-lot coordinate."""
    output = _out(_connection)
    try:
        import services
        data = neighbor_preview.load_capture()
        obj = neighbor_preview.preview_one(data, index, services)
        output("Objeto experimental criado (ID {}). NAO SALVE. Use on.preview_cleanup.".format(
            _safe(lambda: obj.id)))
        diag.log("preview_one:", "index={}".format(index), "id={}".format(_safe(lambda: obj.id)))
    except Exception as exc:
        output("preview_one falhou: {!r}".format(exc))
        diag.log_exception("preview_one", exc)


@sims4.commands.Command("open_neighborhood.preview_shift", "on.preview_shift", command_type=LIVE)
def preview_shift(index: int = 0, offset_x: int = 2, offset_z: int = 0, _connection=None):
    """Create one visibly displaced off-lot copy, then remove with cleanup."""
    output = _out(_connection)
    try:
        import services
        if offset_x == 0 and offset_z == 0:
            raise ValueError("use um deslocamento diferente de zero")
        data = neighbor_preview.load_capture()
        item = neighbor_preview.selected(data, index, services)
        target = neighbor_preview.shifted_position(item, offset_x, offset_z)
        obj = neighbor_preview.preview_one(data, index, services, offset_x, offset_z)
        actual = _safe(lambda: [obj.position.x, obj.position.y, obj.position.z])
        output("Copia deslocada criada (ID {}). Procure fora do local original.".format(
            _safe(lambda: obj.id)))
        output("Nao salve! Depois use on.preview_cleanup.")
        diag.log("preview_shift:", "index={}".format(index),
                 "offset_x={}".format(offset_x), "offset_z={}".format(offset_z),
                 "target={}".format(target), "actual={}".format(actual),
                 "id={}".format(_safe(lambda: obj.id)))
    except Exception as exc:
        output("preview_shift falhou: {!r}".format(exc))
        diag.log_exception("preview_shift", exc)


@sims4.commands.Command("open_neighborhood.preview_cleanup", "on.preview_cleanup", command_type=LIVE)
def preview_cleanup(_connection=None):
    """Attempt removal of all objects created by THIS preview feature."""
    output = _out(_connection)
    removed, remaining = neighbor_preview.cleanup()
    output("Previews removidos: {} | nao removidos: {}".format(removed, remaining))
    diag.log("preview_cleanup:", "removed={}".format(removed), "remaining={}".format(remaining))
