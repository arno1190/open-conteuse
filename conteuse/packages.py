"""Bounded immutable packs and crash-safe local library activation.

Approval records are trusted local parent decisions, not signatures. Transport
must authenticate separately. Directories passed here belong to the studio.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from .manifest import validate

MAX_ASSET = 32 * 1024 * 1024
MAX_TOTAL = 128 * 1024 * 1024
MAX_MANIFEST = 1024 * 1024
HEX = re.compile(r"[0-9a-f]{64}\Z")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def revision(pack):
    return hashlib.sha256(canonical(pack)).hexdigest()


def safe_path(name):
    return (isinstance(name, str) and bool(name) and "\\" not in name
            and not name.startswith("/") and all(p not in ("", ".", "..") for p in name.split("/"))
            and not any(ord(c) < 32 or c == ":" for c in name))


def read_manifest(root):
    path = Path(root) / "manifest.json"
    if path.is_symlink() or path.stat().st_size > MAX_MANIFEST:
        raise ValueError("unsafe or oversized manifest")
    with path.open("rb") as stream:
        data = stream.read(MAX_MANIFEST + 1)
    if len(data) > MAX_MANIFEST:
        raise ValueError("oversized manifest")
    return json.loads(data.decode("utf-8"))


def asset_digest(path, size, output=None):
    """Hash/copy exactly the declared bytes, even if the source grows."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        remaining = size
        while remaining:
            chunk = stream.read(min(65536, remaining))
            if not chunk:
                raise ValueError("truncated asset")
            remaining -= len(chunk)
            digest.update(chunk)
            if output is not None:
                output.write(chunk)
        if stream.read(1):
            raise ValueError("oversized asset")
    return digest.hexdigest()


def check_pack(root):
    root = Path(root).resolve()
    pack = read_manifest(root)
    errors = validate(pack)
    assets = pack.get("assets", []) if isinstance(pack, dict) else []
    if not isinstance(assets, list):
        raise ValueError("assets must be a list")
    names, total = set(), 0
    for asset in assets:
        if not isinstance(asset, dict):
            errors.append("asset must be object")
            continue
        name, size, digest = asset.get("path"), asset.get("size"), asset.get("sha256")
        if not safe_path(name) or name == "manifest.json" or name in names:
            errors.append("unsafe, duplicate or reserved asset path")
            continue
        names.add(name)
        if type(size) is not int or not 0 < size <= MAX_ASSET or not isinstance(digest, str) or not HEX.fullmatch(digest):
            errors.append(f"invalid size/hash: {name}")
            continue
        total += size
        path = root / name
        # Reject symlinks at every level, including links that stay inside root.
        if any(p.is_symlink() for p in [path, *path.parents] if p != root.parent):
            errors.append(f"symlink: {name}")
            continue
        try:
            if not path.is_file() or path.stat().st_size != size:
                raise ValueError("size")
            actual = asset_digest(path, size)
            if actual != digest:
                raise ValueError("hash")
        except (OSError, ValueError):
            errors.append(f"missing or changed asset: {name}")
    if total > MAX_TOTAL:
        errors.append("pack quota exceeded")
    for node in pack.get("nodes", []) if isinstance(pack, dict) else []:
        if isinstance(node, dict) and "audio" in node and (not isinstance(node["audio"], str) or node["audio"] not in names):
            errors.append("unknown audio asset")
    if errors:
        raise ValueError("; ".join(errors))
    return pack


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(dir=path.parent, prefix=".pending-")
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(canonical(value))
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def activate(source, library, approved_revision, interrupt=False):
    """Stage by copy, verify again, then atomically replace active pointer.

    Single writer contract. interrupt is a deterministic power-loss test hook.
    Old immutable versions and unrelated cards/bookmarks are retained.
    """
    pack = check_pack(source)
    digest = revision(pack)
    if approved_revision != digest:
        raise ValueError("final approval does not match content revision")
    library = Path(library)
    versions = library / "versions"
    versions.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=library, prefix="stage-") as stage:
        atomic_json(Path(stage) / "manifest.json", pack)
        for asset in pack.get("assets", []):
            dest = Path(stage) / asset["path"]
            dest.parent.mkdir(parents=True, exist_ok=True)
            with dest.open("wb") as stream:
                digest_copy = asset_digest(Path(source) / asset["path"], asset["size"], stream)
                if digest_copy != asset["sha256"]:
                    raise ValueError("asset changed during staging")
                stream.flush()
                os.fsync(stream.fileno())
        staged = check_pack(stage)
        if revision(staged) != digest:
            raise ValueError("staging changed")
        if interrupt:
            raise InterruptedError("simulated transfer interruption")
        destination = versions / digest
        if destination.exists():
            if revision(check_pack(destination)) != digest:
                raise ValueError("corrupt stored version")
        else:
            # Persist all staged directory entries before the activation pointer.
            for directory_path, _, _ in os.walk(stage, topdown=False):
                directory_fd = os.open(directory_path, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            os.rename(stage, destination)
            directory_fd = os.open(versions, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
        current = library / "active.json"
        if current.exists():
            try:
                previous = json.loads(current.read_text())
                previous_digest = previous["revision"]
                if HEX.fullmatch(previous_digest) and revision(check_pack(versions / previous_digest)) == previous_digest:
                    atomic_json(library / "previous.json", previous)
            except (OSError, ValueError, KeyError, TypeError):
                pass
        atomic_json(current, {"revision": digest})
    return digest


def active_pack(library):
    """Try current, then a verified previous pointer on corruption/restart."""
    library = Path(library)
    for pointer in ("active.json", "previous.json"):
        try:
            digest = json.loads((library / pointer).read_text())["revision"]
            if not isinstance(digest, str) or not HEX.fullmatch(digest):
                continue
            pack = check_pack(library / "versions" / digest)
            if revision(pack) == digest:
                return pack
        except (OSError, ValueError, KeyError, TypeError):
            continue
    raise ValueError("no verified active or previous library")
