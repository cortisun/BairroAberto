#!/usr/bin/env python3
"""Builds dist/OpenNeighborhood.ts4script. MUST run under Python 3.7.x (the game's version).

    <python37>\\python.exe build.py            # build + verify
    <python37>\\python.exe build.py --install "C:\\...\\The Sims 4\\Mods"   # copy only after verify passes

Layout produced (no parent folder, forward slashes, stored, .pyc only):
    open_neighborhood/__init__.pyc
    open_neighborhood/commands.pyc
    open_neighborhood/diag.pyc
"""
import argparse
import importlib.util
import os
import py_compile
import shutil
import sys
import tempfile
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
DIST = os.path.join(HERE, "dist")
NAME = "OpenNeighborhood.ts4script"
PY37_MAGIC = b"\x42\x0d\x0d\x0a"


def require_py37():
    if sys.version_info[:2] != (3, 7) or importlib.util.MAGIC_NUMBER != PY37_MAGIC:
        sys.exit("build.py must run under Python 3.7 (running {}, magic {!r}). "
                 "Use the portable 3.7.9 runtime.".format(sys.version.split()[0], importlib.util.MAGIC_NUMBER))


def build():
    require_py37()
    os.makedirs(DIST, exist_ok=True)
    target = os.path.join(DIST, NAME)
    with tempfile.TemporaryDirectory() as tmp:
        entries = []
        for root, dirs, files in os.walk(SRC):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for fname in sorted(files):
                if not fname.endswith(".py"):
                    continue
                src = os.path.join(root, fname)
                rel = os.path.relpath(src, SRC).replace(os.sep, "/")       # open_neighborhood/x.py
                arc = rel[:-3] + ".pyc"
                out = os.path.join(tmp, arc.replace("/", os.sep))
                os.makedirs(os.path.dirname(out), exist_ok=True)
                py_compile.compile(src, cfile=out, dfile=rel, doraise=True,
                                   invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP)
                entries.append((arc, out))
        if not entries:
            sys.exit("no sources found in " + SRC)
        partial = target + ".partial"
        with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_STORED) as zf:
            for arc, out in entries:
                zi = zipfile.ZipInfo(arc, date_time=(2026, 1, 1, 0, 0, 0))
                zi.compress_type = zipfile.ZIP_STORED
                zi.external_attr = 0o644 << 16
                with open(out, "rb") as fh:
                    zf.writestr(zi, fh.read())
        os.replace(partial, target)
    print("built", target)
    return target


def verify(path):
    sys.path.insert(0, HERE)
    import verify_ts4script
    return verify_ts4script.main([path]) == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", metavar="MODS_DIR", help="copy into this Mods folder after verification")
    args = ap.parse_args()
    target = build()
    if not verify(target):
        sys.exit("verification FAILED - not installing")
    if args.install:
        mods = args.install
        if not os.path.basename(os.path.normpath(mods)).lower() == "mods":
            sys.exit("--install must point at the Mods folder itself (scripts load at most 1 subfolder deep)")
        old = os.path.join(mods, NAME)
        if os.path.exists(old):
            shutil.copy2(old, old + ".bak")
        shutil.copy2(target, old)
        print("installed", old)


if __name__ == "__main__":
    main()
