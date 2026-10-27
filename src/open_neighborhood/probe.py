"""Safe, bounded neighborhood observations for the OpenNeighborhood prototype.

This module does not load neighbor zones or instantiate any game objects. It
accepts a `services`-like object to allow unit testing outside The Sims 4.
"""

MAX_LOTS = 32
MAX_FIELD_NAMES = 48
LOT_FIELDS = (
    "zone_instance_id", "lot_instance_id", "lot_description_id",
    "household_id", "owner_household_id", "lot_name", "name",
    "lot_type", "lot_template_id", "world_id", "neighborhood_id",
)
ZONE_FIELDS = (
    "zone_id", "zone_instance_id", "world_id", "neighborhood_id",
    "lot_id", "lot_description_id", "household_id",
)


def safe_attr(obj, name, default="<ausente>"):
    """Safely read one attribute; never serialize the entire game object."""
    if obj is None:
        return default
    try:
        value = getattr(obj, name)
    except AttributeError:
        return default
    except Exception as exc:
        return "<erro {}>".format(type(exc).__name__)
    if value is None:
        return "<vazio>"
    if isinstance(value, (bool, int, float)):
        return str(value)
    if isinstance(value, str):
        return value[:120].replace("\n", " ").replace("\r", " ")
    # Avoid repr(value): for engine objects it can be expensive or unsafe.
    return "<{}>".format(type(value).__name__)


def _call(obj, name, *args):
    """Return (result, error). Caller must choose only observational APIs."""
    try:
        return getattr(obj, name)(*args), None
    except Exception as exc:
        return None, "{}: {}".format(type(exc).__name__, str(exc)[:160])


def fields(record):
    """Protobuf descriptor names; no serialization or enum iteration."""
    try:
        descriptor = getattr(record, "DESCRIPTOR", None)
        if descriptor is None:
            return []
        raw = getattr(descriptor, "fields", ())
        return [str(field.name) for field in list(raw)[:MAX_FIELD_NAMES]]
    except Exception:
        return []


def _neighborhood(services):
    zone, error = _call(services, "current_zone")
    if error or zone is None:
        return None, None, "current_zone: {}".format(error or "vazio")
    neighborhood_id = getattr(zone, "neighborhood_id", None)
    if neighborhood_id is None:
        return zone, None, "current_zone.neighborhood_id ausente"
    persistence, error = _call(services, "get_persistence_service")
    if error or persistence is None:
        return zone, None, "persistence: {}".format(error or "vazio")
    proto, error = _call(persistence, "get_neighborhood_proto_buff", neighborhood_id)
    if error or proto is None:
        return zone, None, "neighborhood proto: {}".format(error or "vazio")
    return zone, proto, None


def _manager_ids(services):
    manager, error = _call(services, "get_zone_manager")
    if error or manager is None:
        return None, "ZoneManager: {}".format(error or "vazio")
    try:
        ids = list(manager.keys())
    except Exception as exc:
        return None, "ZoneManager.keys: {}".format(type(exc).__name__)
    return ids[:MAX_LOTS * 4], None


def overview(services):
    """Summarize all known lots in the active neighborhood; read-only."""
    lines = ["=== OpenNeighborhood: mapa de lotes (somente leitura) ==="]
    zone, proto, error = _neighborhood(services)
    if error:
        return lines + [error]
    current, current_error = _call(services, "current_zone_id")
    if current_error:
        current = None
    lines.append("zone_atual={} bairro={} mundo={}".format(
        current if current is not None else "?",
        safe_attr(zone, "neighborhood_id"), safe_attr(zone, "world_id")))
    manager_ids, manager_error = _manager_ids(services)
    if manager_error:
        lines.append(manager_error)
    else:
        lines.append("zones_instanciadas={} IDs={}".format(
            len(manager_ids), ", ".join(str(i) for i in manager_ids[:16])))
    try:
        lots = getattr(proto, "lots", None)
        total = len(lots) if lots is not None else 0
    except Exception as exc:
        return lines + ["propriedade lots indisponivel: {}".format(type(exc).__name__)]
    lines.append("lotes_no_bairro={}; limite_relatorio={}".format(total, MAX_LOTS))
    if total:
        lines.append("campos_proto_lote=" + ", ".join(fields(lots[0])))
    for lot in lots[:MAX_LOTS] if lots is not None else ():
        target_id = safe_attr(lot, "zone_instance_id")
        target_num = None
        try:
            target_num = int(target_id)
        except (ValueError, TypeError):
            pass
        loaded = "?" if manager_ids is None else str(target_num in manager_ids)
        lines.append("zona={} lote={} ativo={} instanciado={}".format(
            target_id, safe_attr(lot, "lot_instance_id"),
            target_num == current, loaded))
    if total > MAX_LOTS:
        lines.append("[{} lotes omitidos]".format(total - MAX_LOTS))
    return lines


def inspect_neighbor(services, target_id):
    """Read persisted metadata for a target lot; no travel or zone creation."""
    lines = ["=== OpenNeighborhood: inspecao da zona {} ===".format(target_id)]
    zone, proto, error = _neighborhood(services)
    if error:
        return lines + [error]
    try:
        lots = getattr(proto, "lots", ())
    except Exception as exc:
        return lines + ["erro lendo lotes: {}".format(type(exc).__name__)]
    target = None
    for lot in lots:
        try:
            if int(getattr(lot, "zone_instance_id")) == int(target_id):
                target = lot
                break
        except (ValueError, TypeError, AttributeError):
            continue
    if target is None:
        return lines + ["zona nao encontrada no bairro atual"]
    manager_ids, error = _manager_ids(services)
    lines.append("instanciada={} (True significa zona presente no ZoneManager)".format(
        "?" if manager_ids is None else int(target_id) in manager_ids))
    if error:
        lines.append(error)
    lines.append("campos_do_registro=" + ", ".join(fields(target)))
    for field in LOT_FIELDS:
        lines.append("{}={}".format(field, safe_attr(target, field)))
    lines.append("zona_atual: bairro={} mundo={}".format(
        safe_attr(zone, "neighborhood_id"), safe_attr(zone, "world_id")))
    return lines
