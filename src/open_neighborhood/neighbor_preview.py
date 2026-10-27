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
    if getattr(obj, "is_sim", False):
        return True
    if getattr(obj, "parent", None) is not None:
        return True
    if getattr(obj, "is_in_inventory", False):
        return True
    return False


def snapshot_object(obj):
    """Return purely serializable object data or None for unsuitable objects."""
    try:
        if _is_sim_or_attached(obj):
            return None
        definition_id = _integer(obj.definition.id)
        if not definition_id:
            return None
        location = obj.location
        transform = location.transform
        position = transform.translation
        rotation = transform.orientation
        routing_surface = getattr(location, "routing_surface", None)
        level = _integer(getattr(routing_surface, "secondary_id", 0))
        surface_type = _integer(getattr(routing_surface, "type", 0))
        if level > 10 or surface_type > 100:
            return None
        coords = [_number(getattr(position, key)) for key in ("x", "y", "z")]
        quaternion = [_number(getattr(rotation, key)) for key in ("x", "y", "z", "w")]
        if sum(x*x for x in quaternion) < 0.01:
            return None
        label = str(obj)
        return {"definition_id": definition_id, "position": coords,
                "rotation": quaternion, "level": level,
                "surface_type": surface_type, "label": label[:100]}
    except (AttributeError, TypeError, ValueError, OverflowError):
        return None


def capture(services):
    """Capture a sample of placed objects in the *currently loaded* lot."""
    zone = services.current_zone()
    current_id = _integer(services.current_zone_id())
    neighborhood_id = _integer(zone.neighborhood_id)
    world_id = _integer(zone.world_id)
    manager = services.object_manager()
    objects = []
    skipped = 0
    for obj in manager.values():
        record = snapshot_object(obj)
        if record is None:
            skipped += 1
            continue
        objects.append(record)
        if len(objects) >= MAX_OBJECTS:
            break
    if not objects:
        raise ValueError("nenhum objeto elegivel encontrado no lote atual")
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


def preview_one(data, index, services):
    """Attempt one reversible, explicitly requested, off-lot object preview.

    The engine can reject off-lot objects and native APIs may vary by patch.
    Never mutate the source neighbor objects or their persistent records.
    """
    if _preview_objects:
        raise ValueError("use on.preview_cleanup antes de outra tentativa")
    item = selected(data, index, services)

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
    xyz = item["position"]
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
