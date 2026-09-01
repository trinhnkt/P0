#!/usr/bin/env python3
"""The 5 missing A9 seed-42 jobs on local data/ (junyi + xes3g5m)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(".").resolve()
TEST_N = {
    "junyi": 3_269_022,
    "xes3g5m": 1_589_145,
}

JOBS = [
    ("junyi", "t100", "dkt", 42),
    ("junyi", "t50", "dkt", 42),
    ("xes3g5m", "t50", "dkt", 42),
    ("xes3g5m", "t100", "simplekt", 42),
    ("xes3g5m", "t50", "simplekt", 42),
]


def pred_path(ds, level, model, seed):
    return ROOT / "results" / "predictions" / f"a9_{ds}_learner_based_{model}_{level}_seed{seed}.csv"


def n_rows(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for _ in f) - 1


def is_complete(ds, path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 10_000:
        return False
    return n_rows(path) >= TEST_N[ds]


def main():
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    n_ok = n_skip = n_fail = 0
    for ds, level, model, seed in JOBS:
        out = pred_path(ds, level, model, seed)
        if is_complete(ds, out):
            print(f"SKIP complete {out.name} rows={n_rows(out)}", flush=True)
            n_skip += 1
            continue
        if out.exists():
            print(f"REMOVE truncated {out.name}", flush=True)
            out.unlink()
        cmd = [
            sys.executable, "-u",
            str(ROOT / "scripts" / "a9_train.py"),
            "--dataset", ds,
            "--level", level,
            "--model", model,
            "--seed", str(seed),
            "--batch-size", "32" if model == "simplekt" else "64",
        ]
        print("RUN", " ".join(cmd), flush=True)
        r = subprocess.run(cmd, cwd=ROOT, env=env)
        if r.returncode != 0:
            print("FAILED", ds, level, model, seed, flush=True)
            n_fail += 1
            continue
        if not is_complete(ds, out):
            print("INCOMPLETE after run", out.name, flush=True)
            n_fail += 1
            continue
        n_ok += 1
    print(f"A9 five-job queue done ok={n_ok} skip={n_skip} fail={n_fail}", flush=True)
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
