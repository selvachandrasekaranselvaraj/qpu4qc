"""Content-addressed caching - the "compute once, reuse everywhere" contract.

The real system hashes an entire computation graph (structure, level, every
parameter that could change the answer) into one address, so a result is
never recomputed - not in the same run, not in a later one, not by a
different part of a campaign asking the same question. This toy version
does the same thing for a single (level, x) pair: enough to demonstrate the
property (see `test_cache_hit_avoids_recomputation` in the demo/tests) that
carries over unchanged when the address also covers a real structure's
geometry, a DFT convergence parameter, or a quantum circuit's qubit mapping.
"""
from __future__ import annotations

import hashlib
from typing import Any, Callable


class ContentAddressedCache:
    def __init__(self):
        self._store: dict[str, Any] = {}
        self.hits = 0
        self.misses = 0

    @staticmethod
    def address(level_name: str, x: float) -> str:
        payload = f"{level_name}:{x!r}".encode()
        return hashlib.sha256(payload).hexdigest()

    def get_or_compute(self, level_name: str, x: float, compute: Callable[[], Any]) -> Any:
        addr = self.address(level_name, x)
        if addr in self._store:
            self.hits += 1
            return self._store[addr]
        self.misses += 1
        value = compute()
        self._store[addr] = value
        return value

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total else 0.0
