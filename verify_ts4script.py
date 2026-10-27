#!/usr/bin/env python3
"""Checks a .ts4script before it goes into the Mods folder.

Runs on any Python 3.6+ (no need to be 3.7). Exit code 0 = OK, 1 = problems found.

    python verify_ts4script.py OpenNeighborhood.ts4script
    python verify_ts4script.py OpenNeighborhood.ts4script --compare SomeWorkingMod.ts4script
    python verify_ts4script.py OpenNeighborhood.ts4script --resource-cfg "...\\Mods\\Resource.cfg"
"""
import argparse
import os
import struct
import sys
import zipfile

PY37_MAGIC = b"\x42\x0d\x0d\x0a"  # CPython 3.7 bytecode, magic number 3394
KNOWN_MAGIC = {
    b"\x33\x0d\x0d\x0a": "3.6", PY37_MAGIC: "3.7", b"\x55\x0d\x0d\x0a": "3.8",
    b"\x61\x0d\x0d\x0a": "3.9", b"\x6f\x0d\x0d\x0a": "3.10", b"\xa7\x0d\x0d\x0a": "3.11",
    b"\xcb\x0d\x0d\x0a": "3.12", b"\xf3\x0d\x0d\x0a": "3.13",
}
COMPRESSION = {0: "stored", 8: "deflate", 12: "bzip2", 14: "lzma", 93: "zstd"}


def inspect(path):
    """Returns (errors, warnings, info) for one archive."""
    errors, warnings, info = [], [], {}
    if not os.path.isfile(path):
        return ["file not found: {}".format(path)], warnings, info
    with open(path, "rb") as fh:
        data = fh.read()
    info["size"] = len(data)
    if data[:4] == b"DBPF":
        errors.append("file is a DBPF .package, not a ZIP")
        return errors, warnings, info
    if data[:4] != b"PK\x03\x04":
        errors.append("does not start with a ZIP local header (first bytes {!r})".format(data[:8]))
    if data.find(b"PK\x06\x06") != -1 or data.find(b"PK\x06\x07") != -1:
        errors.append("ZIP64 records present")
    eocd = data.rfind(b"PK\x05\x06")
    if eocd == -1:
        errors.append("no end-of-central-directory record (truncated file?)")
        return errors, warnings, info
    comment_len = struct.unpack("<H", data[eocd + 20:eocd + 22])[0]
    if eocd + 22 + comment_len != len(data):
        warnings.append("bytes after the ZIP end record ({} extra)".format(len(data) - eocd - 22 - comment_len))

    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as exc:
        errors.append("zipfile cannot open it: {}".format(exc))
        return errors, warnings, info
    with zf:
        bad = zf.testzip()
        if bad:
            errors.append("CRC error in {}".format(bad))
        names = []
        methods = set()
        magics = {}
        for zi in zf.infolist():
            name = zi.filename
            names.append(name)
            methods.add(COMPRESSION.get(zi.compress_type, str(zi.compress_type)))
            if "\\" in name:
                errors.append("backslash in entry name: {!r} (PowerShell Compress-Archive bug)".format(name))
            if name.startswith("/") or ":" in name or ".." in name.split("/"):
                errors.append("unsafe/absolute entry name: {!r}".format(name))
            if zi.flag_bits & 0x1:
                errors.append("encrypted entry: {}".format(name))
            if zi.flag_bits & 0x8:
                warnings.append("data-descriptor flag on {} (streamed ZIP)".format(name))
            if zi.compress_type not in (0, 8):
                errors.append("unsupported compression {} on {}".format(zi.compress_type, name))
            if name.endswith(".pyc"):
                head = zf.read(name)[:16]
                magics[name] = KNOWN_MAGIC.get(head[:4], repr(head[:4]))
                if head[:4] != PY37_MAGIC:
                    errors.append("{} was compiled for Python {} (game needs 3.7)".format(name, magics[name]))
                elif len(head) < 16:
                    errors.append("{} header shorter than 16 bytes".format(name))
        if len(set(names)) != len(names):
            errors.append("duplicate entry names")

        files = [n for n in names if not n.endswith("/")]
        top = sorted({n.split("/")[0] for n in files})
        packages = sorted({n.split("/")[0] for n in files
                           if n.count("/") == 1 and n.split("/")[1] in ("__init__.pyc", "__init__.py")})
        modules = sorted(n for n in files if "/" not in n and n.endswith((".pyc", ".py")))
        if not packages and not modules:
            errors.append("no importable top-level package/module. Top level is {} - the zip probably "
                          "contains an extra parent folder (it must hold open_neighborhood/__init__.pyc "
                          "at the root)".format(top))
        for n in files:
            if n.endswith((".pyc", ".py")) and n.split("/")[0] not in packages and "/" in n:
                warnings.append("{} is not inside an importable package".format(n))
        if any(n.endswith(".py") for n in files):
            warnings.append("contains .py sources (fine, but release builds normally ship .pyc only)")
        info.update(entries=len(names), compression=sorted(methods), top_level=top,
                    packages=packages, modules=modules, pyc_versions=sorted(set(magics.values())))
    return errors, warnings, info


def check_resource_cfg(path):
    issues = []
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as fh:
            for i, line in enumerate(fh, 1):
                if "ts4script" in line.lower():
                    issues.append("Resource.cfg line {} mentions .ts4script: {!r}. A PackedFile rule makes "
                                  "the engine read the ZIP as a .package and report it as corrupted."
                                  .format(i, line.strip()))
    except OSError as exc:
        issues.append("cannot read Resource.cfg: {}".format(exc))
    return issues


def report(label, path):
    errors, warnings, info = inspect(path)
    print("== {}: {}".format(label, path))
    for k, v in info.items():
        print("   {:<13} {}".format(k, v))
    for w in warnings:
        print("   WARN  " + w)
    for e in errors:
        print("   ERROR " + e)
    print("   result: {}".format("OK" if not errors else "FAILED ({} errors)".format(len(errors))))
    return errors


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("archive")
    ap.add_argument("--compare", action="append", default=[], help="a known-good .ts4script for comparison")
    ap.add_argument("--resource-cfg", help="path to Mods\\Resource.cfg to check for .ts4script rules")
    args = ap.parse_args(argv)
    errors = report("target", args.archive)
    for ref in args.compare:
        report("reference", ref)
    if args.resource_cfg:
        cfg = check_resource_cfg(args.resource_cfg)
        for c in cfg:
            print("   ERROR " + c)
        errors += cfg
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
