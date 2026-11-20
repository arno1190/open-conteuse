"""Draft text-story graph checks; not a publication authorisation boundary."""


def validate(pack):
    """Return human-readable errors for a draft manifest without mutating it."""
    if not isinstance(pack, dict):
        return ["manifest must be an object"]
    errors = []
    if type(pack.get("format_version")) is not int or pack["format_version"] != 1:
        errors.append("format_version must be integer 1")
    for field in ("id", "title", "start"):
        if not isinstance(pack.get(field), str) or not pack[field].strip():
            errors.append(f"{field} must be a non-empty string")
    nodes = pack.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        return errors + ["nodes must be a non-empty list"]
    graph = {}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            errors.append(f"node {index} must be an object")
            continue
        key = node.get("id")
        if not isinstance(key, str) or not key.strip():
            errors.append(f"node {index} needs a non-empty id")
            continue
        if key in graph:
            errors.append(f"duplicate node: {key}")
        graph[key] = []
        if not isinstance(node.get("text"), str) or not node["text"].strip():
            errors.append(f"node {key} needs text")
        choices = node.get("choices", [])
        if not isinstance(choices, list):
            errors.append(f"node {key} choices must be a list")
            continue
        for choice in choices:
            if not isinstance(choice, dict):
                errors.append(f"node {key} choice must be an object")
                continue
            if not isinstance(choice.get("label"), str) or not choice["label"].strip():
                errors.append(f"node {key} choice needs label")
            target = choice.get("target")
            if not isinstance(target, str) or not target.strip():
                errors.append(f"node {key} choice needs target")
            else:
                graph[key].append(target)
    for key, targets in graph.items():
        for target in targets:
            if target not in graph:
                errors.append(f"node {key} references missing node {target}")
    start = pack.get("start")
    if not isinstance(start, str) or start not in graph:
        errors.append("start must reference an existing node")
    else:
        seen, pending = set(), [start]
        while pending:
            current = pending.pop()
            if current in seen or current not in graph:
                continue
            seen.add(current)
            pending.extend(graph[current])
        for key in sorted(graph.keys() - seen):
            errors.append(f"unreachable node: {key}")
    # Every reachable node must have a path to a terminal node. Optional loops
    # with an exit remain useful; a closed strongly connected region is trapped.
    # Visit each edge once; repeated full scans block the local studio on long
    # otherwise-valid playlists. Missing targets are reported above.
    reverse = {key: [] for key in graph}
    for key, targets in graph.items():
        for target in targets:
            if target in reverse:
                reverse[target].append(key)
    escaping = {key for key, targets in graph.items() if not targets}
    pending = list(escaping)
    while pending:
        for predecessor in reverse[pending.pop()]:
            if predecessor not in escaping:
                escaping.add(predecessor)
                pending.append(predecessor)
    for key in sorted(graph.keys() - escaping):
        errors.append(f"trapped node: {key}")
    return errors
