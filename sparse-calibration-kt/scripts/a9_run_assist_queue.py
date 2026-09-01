#!/usr/bin/env python3
"""Sequential A9 GPU queue. Official prediction files are not overwritten."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(".").resolve()
LOG = ROOT / "logs" / "a9_train.log"
LOG.parent.mkdir(parents=True, exist_ok=True)

# Primary instantiation: ASSISTments, seed 42, both models, three reduced targets.
JOBS = [
    ("assist2012", "t500", "dkt", 42),
    ("assist2012", "t500", "simplekt", 42),
    ("assist2012", "t100", "dkt", 42),
    ("assist2012", "t100", "simplekt", 42),
    ("assist2012", "t50", "dkt", 42),
    ("assist2012", "t50", "simplekt", 42),
]


def main():
    extra = sys.argv[1:]
    with LOG.open("a", encoding="utf-8") as f:
        f.write("\n=== A9 queue start ===\n")
    for ds, level, model, seed in JOBS:
        cmd = [
            sys.executable,
            str(ROOT / "scripts" / "a9_train.py"),
            "--dataset", ds,
            "--level", level,
            "--model", model,
            "--seed", str(seed),
            *extra,
        ]
        print("RUN", " ".join(cmd), flush=True)
        r = subprocess.run(cmd, cwd=ROOT)
        if r.returncode != 0:
            print("FAILED", cmd, "code", r.returncode)
            sys.exit(r.returncode)
    print("A9 assist2012 seed-42 queue complete")


if __name__ == "__main__":
    main()
