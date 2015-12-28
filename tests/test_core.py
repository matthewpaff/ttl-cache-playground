from pathlib import Path
import unittest

from cache_lab.core import replay_cache
from cache_lab.fixture_check import check


class CacheTests(unittest.TestCase):
    def test_null_hit_and_expiry_boundary(self):
        result = replay_cache({"operations": [{"op": "put", "key": "a", "value": None, "ttl": 2}, {"op": "get", "key": "a"}, {"op": "advance", "seconds": 2}, {"op": "get", "key": "a"}]})
        self.assertTrue(result["results"][1]["hit"])
        self.assertFalse(result["results"][3]["hit"])
        self.assertEqual(result["keys"], [])

    def test_reads_update_lru_position(self):
        result = replay_cache({"capacity": 2, "operations": [{"op": "put", "key": "a", "value": 1, "ttl": 10}, {"op": "put", "key": "b", "value": 2, "ttl": 10}, {"op": "get", "key": "a"}, {"op": "put", "key": "c", "value": 3, "ttl": 10}]})
        self.assertEqual((result["results"][-1]["evicted"], result["keys"]), ("b", ["a", "c"]))

    def test_invalid_time_and_capacity(self):
        for data in ({"capacity": True, "operations": []}, {"operations": [{"op": "advance", "seconds": -1}]}, {"operations": [{"op": "put", "key": "a", "value": 1, "ttl": 0}]}):
            with self.assertRaises(ValueError):
                replay_cache(data)

    def test_complete_fixture_corpus(self):
        self.assertGreaterEqual(check(Path(__file__).resolve().parents[1] / "fixtures/cases.jsonl", replay_cache), 350)


if __name__ == "__main__":
    unittest.main()
