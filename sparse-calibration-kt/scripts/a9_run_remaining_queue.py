#!/usr/bin/env python3
"""Remaining A9 GPU jobs: Junyi + XES3G5M, seed 42. Skips existing prediction CSVs."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(".").resolve()

JOBS = []
for model in ("dkt", "simplekt"):
    for level in ("t500", "t100", "t50"):
        JOBS.append(("junyi", level, model, 42))


def pred_path(ds, level, model, seed):
    return ROOT / "results" / "predictions" / f"a9_{ds}_learner_based_{model}_{level}_seed{seed}.csv"


def main():
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    n_ok = n_skip = n_fail = 0
    for ds, level, model, seed in JOBS:
        out = pred_path(ds, level, model, seed)
        if out.exists() and out.stat().st_size > 1000:
            print(f"SKIP {out.name}", flush=True)
            n_skip += 1
            continue
        cmd = [
            sys.executable, "-u",
            str(ROOT / "scripts" / "a9_train.py"),
            "--dataset", ds,
            "--level", level,
            "--model", model,
            "--seed", str(seed),
        ]
        batch = 64
        if model == "simplekt" and ds in {"junyi", "xes3g5m"}:
            batch = 32
        cmd += ["--batch-size", str(batch)]
        print("RUN", " ".join(cmd), flush=True)
        r = subprocess.run(cmd, cwd=ROOT, env=env)
        if r.returncode != 0 and batch != 16:
            print("RETRY batch-size 16", flush=True)
            cmd[-1] = "16"
            r = subprocess.run(cmd, cwd=ROOT, env=env)
        if r.returncode != 0:
            print("FAILED", ds, level, model, seed, flush=True)
            n_fail += 1
            continue
        n_ok += 1
    print(f"A9 remaining queue done ok={n_ok} skip={n_skip} fail={n_fail}", flush=True)
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
