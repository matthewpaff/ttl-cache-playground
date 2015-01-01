# TTL Cache Playground

Replay a small bounded LRU cache using explicit logical time and TTL expiration.

Uses Python 3.10+ and its standard library only. No package installation, virtual
environment, external server, Redis, Celery, or network access is required.

## Run

```console
python -m cache_lab --help
python -m cache_lab examples/sample.json
python -m cache_lab --check-fixtures fixtures/cases.jsonl
python generate_fixtures.py --count 20
python -m unittest discover -s tests -v
```

Run from this directory. The optional path defaults to `-`, which reads JSON from
stdin. Output is JSON or a fixture-check summary. Exit codes are 0 success,
1 file failure, and 2 invalid input. Examples and fixtures contain generated data.

Input has capacity and operations. put sets key, value, and positive ttl; get reports hit separately from value, so cached null is a hit; advance adds explicit nonnegative seconds. Expiration occurs when logical time reaches the deadline. Reads and replacements refresh LRU position; replacements reset TTL. The cache and clock exist only for the current replay. No Redis process, concurrency, or wall-clock waiting is involved.

## Learning focus

The roadmap's 2014–2015 cache-expiration and Redis-inspired learning themes. This is an independent concept exercise based on the modeled
roadmap. It makes no claim to be employer-owned or period-authentic production code.

## Structure

- `cache_lab/core.py`: validated parsing, storage, or state transitions.
- `cache_lab/cli.py`: JSON command interface.
- `cache_lab/generate_fixtures.py`: original deterministic validation cases.
- `cache_lab/fixture_check.py`: expected-output/error checks.
- `fixtures/cases.jsonl`: 367 generated cases, with explicit descriptions.
- `tests/`: independently selected boundaries and the complete corpus check.

Branches `feature/core`, `feature/cli`, `data/fixtures`, and `docs/usage` retain
snapshots; `main` contains the complete tool. Dates and provenance are also recorded
in TIMELINE.json. Many data cases share a scenario; they are not separate features.

Keep changes focused, use actual dates for new work, and add a regression test
for changed behavior. Licensed under [MIT](LICENSE).

[History and provenance](HISTORY.md).
