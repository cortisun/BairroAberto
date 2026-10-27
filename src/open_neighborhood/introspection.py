"""Introspection only; never invoke an unknown Sims 4 native function.

Read-only reports to inspect exported symbols and types of the *active* zone.
"""

import inspect
import re

NATIVE_MODULES = frozenset((
    "_buildbuy", "_placement", "_pathing", "_terrain", "_zone", "_lot",
))
CLASS_KEYWORDS = (
    "load", "lot", "zone", "object", "world", "build", "wall", "room",
    "portal", "route", "nav", "spawn", "manager", "save", "cache",
)
MAX_CLASS_NAMES = 75
MAX_DOC_CHARS = 400


def native_info(modules, module_name, symbol_name):
    """Return metadata about a known native symbol without invoking it."""
    lines = ["=== native_info {}.{} ===".format(module_name, symbol_name)]
    if module_name not in NATIVE_MODULES or not re.match(r"^[A-Za-z_]\w{0,95}$", symbol_name):
        return lines + ["nome de modulo ou simbolo nao permitido"]
    module = modules.get(module_name)
    if module is None:
        return lines + ["modulo nao importado pelo jogo"]
    try:
        target = inspect.getattr_static(module, symbol_name)
    except AttributeError:
        return lines + ["simbolo nao encontrado"]
    except Exception as exc:
        return lines + ["erro ao ler simbolo: {}".format(type(exc).__name__)]
    lines.append("tipo=" + type(target).__name__)
    try:
        lines.append("assinatura=" + str(inspect.signature(target)))
    except (ValueError, TypeError):
        lines.append("assinatura=<nao disponibilizada pela API nativa>")
    except Exception as exc:
        lines.append("assinatura=<erro {}>".format(type(exc).__name__))
    try:
        txt_sig = getattr(target, "__text_signature__", None)
        if txt_sig:
            lines.append("assinatura_texto=" + str(txt_sig)[:MAX_DOC_CHARS])
    except Exception:
        pass
    try:
        doc = inspect.getdoc(target)
        lines.append("documentacao=" + (doc[:MAX_DOC_CHARS] if doc else "<ausente>"))
    except Exception as exc:
        lines.append("documentacao=<erro {}>".format(type(exc).__name__))
    return lines


def class_info(active_zone):
    """Inspect class descriptors for the active zone and its active lot."""
    lines = ["=== Classes ativas (somente leitura) ==="]
    if active_zone is None:
        return lines + ["zona ativa nao encontrada"]
    pairs = [("Zone", active_zone)]
    try:
        active_lot = getattr(active_zone, "lot", None)
    except Exception as exc:
        lines.append("lot indisponivel: {}".format(type(exc).__name__))
        active_lot = None
    if active_lot is not None:
        pairs.append(("Lot", active_lot))
    for label, instance in pairs:
        cls = type(instance)
        lines.append("[{}] classe={}.{}".format(label, cls.__module__, cls.__name__))
        try:
            names = [name for name in sorted(dir(cls))
                     if any(keyword in name.lower() for keyword in CLASS_KEYWORDS)]
        except Exception as exc:
            lines.append("dir falhou: {}".format(type(exc).__name__))
            continue
        lines.append("nomes_relevantes={} (limite={})".format(len(names), MAX_CLASS_NAMES))
        for name in names[:MAX_CLASS_NAMES]:
            try:
                descriptor = inspect.getattr_static(cls, name)
                kind = type(descriptor).__name__
            except Exception as exc:
                kind = "<erro {}>".format(type(exc).__name__)
            lines.append("  {} [{}]".format(name, kind))
        if len(names) > MAX_CLASS_NAMES:
            lines.append("  [{} omitidos]".format(len(names) - MAX_CLASS_NAMES))
    return lines
