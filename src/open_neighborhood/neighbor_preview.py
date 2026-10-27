"""Experimental, opt-in furnishing bridge between two ordinary TS4 lots.

Capture is read-only. A preview duplicates *one* definition into the current
zone, at the recorded world coordinate. This does not load lot architecture,
residents, or a second zone. Never treat the copies as a substitute for save data.
"""
import json
import math
import os

from open_neighborhood import diag

CAPTURE_NAME = "OpenNeighborhood_capture.json"
FORMAT_VERSION = 1
MAX_OBJECTS = 256
MAX_CAPTURE_BYTES = 240000

_preview_objects = []


def capture_path():
    return os.path.join(diag._mods_dir(), CAPTURE_NAME)


def _number(value):
    result = float(value)
    if not math.isfinite(result) or abs(result) > 100000:
        raise ValueError("coordenada invalida")
    return result


def _integer(value):
    if isinstance(value, bool):
        raise ValueError("booleano nao e ID")
    result = int(value)
    if result < 0 or result > 18446744073709551615:
        raise ValueError("ID fora do intervalo")
    return result


def _is_sim_or_attached(obj):
    # Some TS4 versions expose these flags as methods, not properties. A bound
    # method is always truthy, which incorrectly rejected EVERY object in 0.5.0.
    if _flag(obj, "is_sim"):
        return True
    if getattr(obj, "parent", None) is not None:
        return True
    if _flag(obj, "is_in_inventory"):
        return True
    return False


def _flag(obj, name):
    value = getattr(obj, name, False)
    if callable(value):
        try:
            value = value()
        except Exception:
            # Do not treat an uncallable/unsupported optional flag as True.
            # Remaining validation still excludes objects without transforms.
            return False
    return bool(value)


def _objects_from_manager(manager):
    """Get placed objects via the API offered by this game's ObjectManager."""
    getter = getattr(manager, "get_all", None)
    if callable(getter):
        try:
            objects = getter()
            if objects is not None:
                return objects, "get_all"
        except Exception as exc:
            diag.log("ObjectManager.get_all unavailable:", type(exc).__name__)
    getter = getattr(manager, "values", None)
    if callable(getter):
        return getter(), "values"
    raise ValueError("ObjectManager nao oferece get_all nem values")


def snapshot_object(obj, rejected=None):
    """Return purely serializable object data or None for unsuitable objects."""
    def skip(reason):
        if rejected is not None:
            rejected[reason] = rejected.get(reason, 0) + 1
        return None

    try:
        if _is_sim_or_attached(obj):
            return skip("sim_ou_anexado")
        definition = getattr(obj, "definition", None)
        raw_id = getattr(definition, "id", None)
        if raw_id is None:
            raw_id = getattr(obj, "definition_id", 0)
        definition_id = _integer(raw_id)
        if not definition_id:
            return skip("sem_definicao")
        location = getattr(obj, "location", None)
        transform = getattr(location, "transform", None)
        if transform is None:
            transform = getattr(obj, "transform", None)
        if transform is None:
            return skip("sem_transform")
        position = getattr(transform, "translation", None)
        rotation = getattr(transform, "orientation", None)
        if position is None or rotation is None:
            return skip("sem_posicao_ou_rotacao")
        routing_surface = getattr(location, "routing_surface", None)
        if routing_surface is None:
            routing_surface = getattr(obj, "routing_surface", None)
        level = _integer(getattr(routing_surface, "secondary_id", 0))
        surface_type = _integer(getattr(routing_surface, "type", 0))
        if level > 10 or surface_type > 100:
            return skip("superficie_invalida")
        coords = [_number(getattr(position, key)) for key in ("x", "y", "z")]
        quaternion = [_number(getattr(rotation, key)) for key in ("x", "y", "z", "w")]
        if sum(x*x for x in quaternion) < 0.01:
            return skip("rotacao_invalida")
        label = str(obj)
        return {"definition_id": definition_id, "position": coords,
                "rotation": quaternion, "level": level,
                "surface_type": surface_type, "label": label[:100]}
    except (AttributeError, TypeError, ValueError, OverflowError):
        return skip("campo_incompativel")


def capture(services):
    """Capture a sample of placed objects in the *currently loaded* lot."""
    zone = services.current_zone()
    current_id = _integer(services.current_zone_id())
    neighborhood_id = _integer(zone.neighborhood_id)
    world_id = _integer(zone.world_id)
    manager = services.object_manager()
    candidates, source = _objects_from_manager(manager)
    objects = []
    skipped = 0
    scanned = 0
    reasons = {}
    for obj in candidates:
        scanned += 1
        record = snapshot_object(obj, reasons)
        if record is None:
            skipped += 1
            continue
        objects.append(record)
        if len(objects) >= MAX_OBJECTS:
            break
    if not objects:
        raise ValueError("nenhum objeto elegivel; examinados={} via {}; motivos={}".format(
            scanned, source, reasons))
    diag.log("capture scan:", "api={}".format(source),
             "examined={}".format(scanned), "eligible={}".format(len(objects)),
             "skipped={}".format(skipped), "reasons={}".format(reasons))
    return {"format": FORMAT_VERSION, "source_zone_id": current_id,
            "neighborhood_id": neighborhood_id, "world_id": world_id,
            "objects": objects, "skipped": skipped}


def validate(data):
    if not isinstance(data, dict) or data.get("format") != FORMAT_VERSION:
        raise ValueError("arquivo de captura desconhecido")
    for key in ("source_zone_id", "neighborhood_id", "world_id"):
        if _integer(data[key]) <= 0:
            raise ValueError("campo de zona invalido: " + key)
    objects = data["objects"]
    if not isinstance(objects, list) or not (1 <= len(objects) <= MAX_OBJECTS):
        raise ValueError("quantidade de objetos invalida")
    for item in objects:
        if not isinstance(item, dict) or _integer(item["definition_id"]) <= 0:
            raise ValueError("definicao de objeto invalida")
        if len(item["position"]) != 3 or len(item["rotation"]) != 4:
            raise ValueError("transform invalido")
        for coordinate in item["position"] + item["rotation"]:
            _number(coordinate)
        if not 0 <= _integer(item["level"]) <= 10:
            raise ValueError("andar invalido")
        if not 0 <= _integer(item["surface_type"]) <= 100:
            raise ValueError("surface type invalido")
    return data


def save_capture(data):
    payload = json.dumps(validate(data), ensure_ascii=True, indent=1).encode("utf-8")
    if len(payload) > MAX_CAPTURE_BYTES:
        raise ValueError("captura grande demais")
    destination = capture_path()
    temp = destination + ".partial"
    with open(temp, "wb") as target:
        target.write(payload)
    os.replace(temp, destination)
    return destination


def load_capture():
    path = capture_path()
    if os.stat(path).st_size > MAX_CAPTURE_BYTES:
        raise ValueError("arquivo de captura acima do limite")
    with open(path, "r", encoding="utf-8") as target:
        return validate(json.load(target))


def selected(data, index, services):
    validate(data)
    zone = services.current_zone()
    if _integer(services.current_zone_id()) == data["source_zone_id"]:
        raise ValueError("volte para seu lote antes de tentar a visualizacao")
    if (_integer(zone.neighborhood_id) != data["neighborhood_id"] or
            _integer(zone.world_id) != data["world_id"]):
        raise ValueError("a casa capturada nao pertence a este bairro/mundo")
    if not 0 <= index < len(data["objects"]):
        raise ValueError("indice invalido; veja on.captured")
    return data["objects"][index]


def _destroy_preview(obj):
    try:
        obj.destroy(source=obj, cause="OpenNeighborhood preview cleanup")
    except TypeError:
        obj.destroy()


def cleanup():
    """Destroy only objects that THIS mod successfully created and tracked."""
    global _preview_objects
    remaining = []
    removed = 0
    for obj in _preview_objects:
        try:
            _destroy_preview(obj)
            removed += 1
        except Exception as exc:
            remaining.append(obj)
            diag.log_exception("preview cleanup", exc)
    _preview_objects = remaining
    return removed, len(remaining)


def preview_one(data, index, services, offset_x=0, offset_z=0):
    """Attempt one reversible, explicitly requested, off-lot object preview.

    The engine can reject off-lot objects and native APIs may vary by patch.
    Never mutate the source neighbor objects or their persistent records.
    """
    if _preview_objects:
        raise ValueError("use on.preview_cleanup antes de outra tentativa")
    item = selected(data, index, services)
    xyz = shifted_position(item, offset_x, offset_z)

    from objects.system import create_object
    from objects.object_enums import ItemLocation
    from sims4.math import Location, Quaternion, Transform, Vector3
    import routing

    definition = services.definition_manager().get(item["definition_id"])
    if definition is None:
        raise ValueError("definicao indisponivel; talvez falte um pacote/DLC")

    # Use the active-zone surface; the saved surface belongs to a different
    # zone and can't safely be passed through unchanged.
    active_zone_id = services.current_zone_id()
    surface_type = routing.SurfaceType(item["surface_type"])
    surface = routing.SurfaceIdentifier(active_zone_id, item["level"], surface_type)
    q = item["rotation"]
    transform = Transform(Vector3(xyz[0], xyz[1], xyz[2]),
                          Quaternion(q[0], q[1], q[2], q[3]))
    location = Location(transform, surface)

    # Creation itself may add the object to the simulation. Any error after
    # this line must destroy the new object before returning to the caller.
    obj = create_object(definition, loc_type=ItemLocation.ON_LOT)
    if obj is None:
        raise RuntimeError("o jogo recusou criar a definicao")
    try:
        obj.location = location
    except Exception:
        try:
            _destroy_preview(obj)
        except Exception as cleanup_exc:
            # Retain the reference so a later on.preview_cleanup can retry.
            _preview_objects.append(obj)
            diag.log_exception("preview spawn rollback", cleanup_exc)
        raise
    _preview_objects.append(obj)
    return obj


def preview_count():
    return len(_preview_objects)


def shifted_position(record, offset_x=0, offset_z=0):
    """Pure transform used to distinguish a generated copy from vanilla LOD."""
    for value in (offset_x, offset_z):
        if isinstance(value, bool) or not isinstance(value, int) or abs(value) > 3:
            raise ValueError("deslocamento deve ser inteiro entre -3 e 3")
    x, y, z = record["position"]
    return [x + offset_x, y, z + offset_z]
