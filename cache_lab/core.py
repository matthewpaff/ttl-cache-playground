"""Replay cache operations deterministically; never sleep or contact Redis."""
from collections import OrderedDict


def bounded(value, label, low, high):
    if type(value) is not int or not low <= value <= high:
        raise ValueError("{} must be an integer from {} to {}".format(label, low, high))
    return value


def replay_cache(data):
    if not isinstance(data, dict) or not isinstance(data.get("operations"), list) or len(data["operations"]) > 1000:
        raise ValueError("Supply at most 1000 cache operations")
    capacity = bounded(data.get("capacity", 3), "capacity", 1, 100)
    now, entries, results = 0, OrderedDict(), []

    def expire():
        for key in [key for key, (_, expiry) in entries.items() if expiry <= now]:
            del entries[key]

    for operation in data["operations"]:
        if not isinstance(operation, dict):
            raise ValueError("Operation must be an object")
        kind = operation.get("op")
        if kind == "advance":
            if set(operation) != {"op", "seconds"}:
                raise ValueError("Advance needs exactly op and seconds")
            now += bounded(operation["seconds"], "seconds", 0, 86400)
            expire()
            results.append({"op": "advance", "time": now})
            continue
        if kind not in ("put", "get"):
            raise ValueError("Unknown cache operation")
        expected = {"op", "key", "value", "ttl"} if kind == "put" else {"op", "key"}
        if set(operation) != expected:
            raise ValueError("Unexpected or missing cache fields")
        key = operation["key"]
        if not isinstance(key, str) or not 1 <= len(key.strip()) <= 80:
            raise ValueError("Key must contain 1–80 nonblank characters")
        expire()
        if kind == "put":
            ttl = bounded(operation["ttl"], "ttl", 1, 86400)
            evicted = None
            if key in entries:
                del entries[key]
            elif len(entries) >= capacity:
                evicted, _ = entries.popitem(last=False)
            entries[key] = (operation["value"], now + ttl)
            results.append({"op": "put", "key": key, "evicted": evicted})
        else:
            hit = key in entries
            value = entries[key][0] if hit else None
            if hit:
                entries.move_to_end(key)
            results.append({"op": "get", "key": key, "hit": hit, "value": value})
    return {"results": results, "keys": list(entries), "time": now}
