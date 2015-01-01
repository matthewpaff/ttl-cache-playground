"""Original cache replays using explicit logical time, not wall-clock sleeps."""


def put(key, value, ttl=10):
    return {"op": "put", "key": key, "value": value, "ttl": ttl}


def stored(key, evicted=None):
    return {"op": "put", "key": key, "evicted": evicted}


def read(key, hit, value=None):
    return {"op": "get", "key": key, "hit": hit, "value": value}


def make_case(index):
    key, kind = "key-{}".format(index), index % 11
    data = {"capacity": 2, "operations": []}
    if kind == 0:
        data["capacity"] = 0
        description = "reject caches with zero capacity"
    elif kind == 1:
        data["operations"] = [put(key, index, 0)]
        description = "reject zero-length cache TTLs"
    elif kind == 2:
        data["operations"] = [{"op": "advance", "seconds": -1}]
        description = "reject backward logical clock advances"
    elif kind == 3:
        data["operations"] = [{"op": "remove", "key": key}]
        description = "reject unsupported cache operations"
    elif kind == 4:
        data["operations"] = [put(" ", index)]
        description = "reject blank cache keys"
    elif kind == 5:
        data["operations"] = [{"op": "get", "key": key}]
        expected = {"results": [read(key, False)], "keys": [], "time": 0}
        description = "report a miss for an unknown key"
    elif kind == 6:
        data["operations"] = [put(key, None, 3), {"op": "get", "key": key}]
        expected = {"results": [stored(key), read(key, True)], "keys": [key], "time": 0}
        description = "distinguish cached null values from misses"
    elif kind in (7, 8):
        expired = kind == 7
        data["operations"] = [put(key, index, 2 if expired else 3), {"op": "advance", "seconds": 2}, {"op": "get", "key": key}]
        expected = {"results": [stored(key), {"op": "advance", "time": 2}, read(key, not expired, None if expired else index)],
                    "keys": [] if expired else [key], "time": 2}
        description = "expire entries exactly at the TTL boundary" if expired else "retain entries before the TTL boundary"
    elif kind == 9:
        a, b, c = key + "-a", key + "-b", key + "-c"
        data["operations"] = [put(a, 1), put(b, 2), {"op": "get", "key": a}, put(c, 3)]
        expected = {"results": [stored(a), stored(b), read(a, True, 1), stored(c, b)], "keys": [a, c], "time": 0}
        description = "evict the least recently read entry at capacity"
    else:
        data["operations"] = [put(key, index, 2), {"op": "advance", "seconds": 1}, put(key, index + 1, 5),
                              {"op": "advance", "seconds": 1}, {"op": "get", "key": key}]
        expected = {"results": [stored(key), {"op": "advance", "time": 1}, stored(key), {"op": "advance", "time": 2}, read(key, True, index + 1)], "keys": [key], "time": 2}
        description = "renew expiration when replacing a cached value"
    result = {"id": "cache-{:04d}".format(index), "description": description, "input": data}
    result.update({"expected_error": True} if kind < 5 else {"expected": expected})
    return result
