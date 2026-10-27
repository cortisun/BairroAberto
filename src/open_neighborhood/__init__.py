# BairroAberto - experimental off-lot furnishing preview (v0.5.1)
#
# Commands may capture objects and spawn one experimental preview when requested.
# The import itself is wrapped so a failure is logged instead of breaking the loader.

VERSION = "0.5.1"

try:
    from open_neighborhood import diag as _diag
    _diag.on_import()
    from open_neighborhood import commands as _commands  # registers the cheat commands
except Exception as _exc:  # never let an import error escape into the game loader
    try:
        from open_neighborhood import diag as _diag2
        _diag2.log_exception("import failed", _exc)
    except Exception:
        pass
