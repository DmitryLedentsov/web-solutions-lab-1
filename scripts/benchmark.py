from __future__ import annotations

import csv
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
CSV_PATH = DATA_DIR / "measurements.csv"
META_PATH = DATA_DIR / "benchmark_metadata.json"

SIZES = [100_000, 250_000, 500_000, 1_000_000, 2_000_000]
REPEATS = 7
WARMUPS = 1


def workload(n: int) -> int:
    """Simple deterministic O(n) CPU workload."""
    total = 0
    for i in range(n):
        total += (i * i + 3 * i) % 97
    return total


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, int | str]] = []
    checksums: dict[int, int] = {}

    for size in SIZES:
        for _ in range(WARMUPS):
            checksums[size] = workload(size)

        for run in range(1, REPEATS + 1):
            started = time.perf_counter_ns()
            checksum = workload(size)
            elapsed_ms = (time.perf_counter_ns() - started) / 1_000_000
            rows.append(
                {
                    "input_size": size,
                    "run": run,
                    "duration_ms": f"{elapsed_ms:.6f}",
                    "checksum": checksum,
                }
            )
            checksums[size] = checksum

    with CSV_PATH.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["input_size", "run", "duration_ms", "checksum"],
        )
        writer.writeheader()
        writer.writerows(rows)

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version.split()[0],
        "python_implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "sizes": SIZES,
        "repeats": REPEATS,
        "warmups_per_size": WARMUPS,
        "timer": "time.perf_counter_ns",
        "workload": "total += (i * i + 3 * i) % 97 in a Python loop",
        "checksums": checksums,
    }
    META_PATH.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote {CSV_PATH}")
    print(f"Wrote {META_PATH}")


if __name__ == "__main__":
    main()
