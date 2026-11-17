"""Parent-invoked media/playlist import; never treats metadata as instructions."""
import hashlib
from pathlib import Path
import shutil
from .packages import MAX_ASSET, MAX_TOTAL, atomic_json, check_pack
from .feeds import fetch, parse_rss


def import_playlist(files, destination, title="Imported playlist"):
    files, destination = list(map(Path, files)), Path(destination)
    if not files or len(files) > 1000 or not title.strip():
        raise ValueError("playlist needs a title and 1..1000 files")
    if destination.exists():
        raise ValueError("import destination must be new")
    sizes = [p.stat().st_size for p in files]
    if any(not 0 < size <= MAX_ASSET for size in sizes) or sum(sizes) > MAX_TOTAL:
        raise ValueError("import quota exceeded")
    if any(p.suffix.lower() not in (".wav", ".mp3", ".aac", ".m4a") or not p.is_file() or p.is_symlink() for p in files):
        raise ValueError("unsupported input file")
    destination.mkdir(parents=True)
    try:
        pack = {"format_version": 1, "id": "imported-playlist", "title": title,
                "start": "track-0", "nodes": [], "assets": []}
        for i, source in enumerate(files):
            name = f"assets/{i:04d}{source.suffix.lower()}"
            output = destination / name
            output.parent.mkdir(exist_ok=True)
            # Copy bounded bytes rather than blindly copying a file that may grow.
            with source.open("rb") as stream:
                data = stream.read(MAX_ASSET + 1)
            if not 0 < len(data) <= MAX_ASSET:
                raise ValueError("input changed/oversized")
            output.write_bytes(data)
            pack["assets"].append({"path": name, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            node = {"id": f"track-{i}", "text": source.stem, "audio": name}
            if i + 1 < len(files):
                node["choices"] = [{"label": "Next track", "target": f"track-{i+1}"}]
            pack["nodes"].append(node)
        atomic_json(destination / "manifest.json", pack)
        check_pack(destination)
        return pack
    except BaseException:
        shutil.rmtree(destination)
        raise


def download_episode(feed_url, guid, destination):
    """Parent explicitly chooses GUID; download remains unapproved for review."""
    episodes = parse_rss(fetch(feed_url, limit=1024*1024))
    selected = next((ep for ep in episodes if ep["guid"] == guid), None)
    if not selected:
        raise ValueError("episode GUID missing")
    path = Path(destination)
    if path.exists():
        raise ValueError("download destination must be new")
    data = fetch(selected["url"])
    if not data:
        raise ValueError("empty audio")
    # Exclusive creation avoids overwriting a recording or previous episode.
    with path.open("xb") as stream:
        stream.write(data)
    return {**selected, "sha256": hashlib.sha256(data).hexdigest(), "size": len(data),
            "approval": "pending review of downloaded bytes"}
