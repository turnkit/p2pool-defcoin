#!/usr/bin/env python3
"""Benchmark small deterministic caches used by the Defcoin P2Pool port."""

from __future__ import annotations

import statistics
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from p2pool import data as p2pool_data
from p2pool.bitcoin import data as bitcoin_data
from p2pool.networks import defcoin


def _time_calls(func, values, rounds):
    start = time.perf_counter()
    checksum = 0
    for _ in range(rounds):
        for value in values:
            result = func(value)
            if isinstance(result, float):
                checksum ^= int(result)
            else:
                checksum ^= int(result)
    return time.perf_counter() - start, checksum


def _time_tuple_calls(func, values, rounds):
    start = time.perf_counter()
    checksum = 0
    for _ in range(rounds):
        for args in values:
            result = func(*args)
            if isinstance(result, (str, bytes)):
                checksum ^= len(result)
            elif isinstance(result, tuple):
                checksum ^= int(result[0])
            elif isinstance(result, float):
                checksum ^= int(result)
            else:
                checksum ^= int(result)
    return time.perf_counter() - start, checksum


def _format_speedup(uncached, cached):
    if cached == 0:
        return "inf"
    return "%.2fx" % (uncached / cached)


def main():
    targets = [
        2**256 // divisor - 1
        for divisor in (2**20, 2**22, 2**24, 2**26, 2**28, 2**30, 2**32, 2**34)
    ]
    difficulties = [1.0, 2.0, 4.0, 8.0, 16.0, 32.0, 64.0, 128.0]
    address_hashes = [0x1000000000000000000000000000000000000000 + i for i in range(8)]
    address_args = [(value, defcoin.PARENT.ADDRESS_VERSION, -1, defcoin.PARENT) for value in address_hashes]
    addresses = [
        bitcoin_data.pubkey_hash_to_address(value, defcoin.PARENT.ADDRESS_VERSION, -1, defcoin.PARENT)
        for value in address_hashes
    ]
    script_args = [(address, defcoin.PARENT) for address in addresses]

    cases = [
        ("target_to_average_attempts", bitcoin_data.target_to_average_attempts, targets, 20000),
        ("target_to_difficulty", bitcoin_data.target_to_difficulty, targets, 20000),
        ("difficulty_to_target", bitcoin_data.difficulty_to_target, difficulties, 20000),
    ]

    print("cache benchmark: repeated deterministic calculations")
    for name, cached_func, values, rounds in cases:
        cached_func.cache_clear()
        uncached_func = cached_func.__wrapped__
        uncached_times = []
        cached_times = []
        uncached_checksum = cached_checksum = None
        for _ in range(5):
            elapsed, uncached_checksum = _time_calls(uncached_func, values, rounds)
            uncached_times.append(elapsed)
            cached_func.cache_clear()
            elapsed, cached_checksum = _time_calls(cached_func, values, rounds)
            cached_times.append(elapsed)
        assert uncached_checksum == cached_checksum
        uncached = statistics.median(uncached_times)
        cached = statistics.median(cached_times)
        print(
            f"{name} uncached={uncached:.6f}s cached={cached:.6f}s "
            f"speedup={_format_speedup(uncached, cached)} cache={cached_func.cache_info()}"
        )

    tuple_cases = [
        ("pubkey_hash_to_address", bitcoin_data.pubkey_hash_to_address, address_args, 20000),
        ("address_to_script2", bitcoin_data.address_to_script2, script_args, 20000),
    ]
    for name, cached_func, values, rounds in tuple_cases:
        cached_func.cache_clear()
        uncached_func = cached_func.__wrapped__
        uncached_times = []
        cached_times = []
        uncached_checksum = cached_checksum = None
        for _ in range(5):
            elapsed, uncached_checksum = _time_tuple_calls(uncached_func, values, rounds)
            uncached_times.append(elapsed)
            cached_func.cache_clear()
            elapsed, cached_checksum = _time_tuple_calls(cached_func, values, rounds)
            cached_times.append(elapsed)
        assert uncached_checksum == cached_checksum
        uncached = statistics.median(uncached_times)
        cached = statistics.median(cached_times)
        print(
            f"{name} uncached={uncached:.6f}s cached={cached:.6f}s "
            f"speedup={_format_speedup(uncached, cached)} cache={cached_func.cache_info()}"
        )

    p2pool_data.donation_script_to_address.cache_clear()
    start = time.perf_counter()
    for _ in range(10000):
        p2pool_data.donation_script_to_address.__wrapped__(defcoin)
    uncached = time.perf_counter() - start
    start = time.perf_counter()
    for _ in range(10000):
        p2pool_data.donation_script_to_address(defcoin)
    cached = time.perf_counter() - start
    print(
        f"donation_script_to_address uncached={uncached:.6f}s cached={cached:.6f}s "
        f"speedup={_format_speedup(uncached, cached)} "
        f"cache={p2pool_data.donation_script_to_address.cache_info()}"
    )


if __name__ == "__main__":
    main()
