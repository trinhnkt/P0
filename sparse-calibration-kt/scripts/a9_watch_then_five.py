#!/usr/bin/env python3
"""After Junyi DKT t500 is a complete file, stop the Junyi-only parent and run the 5 missing jobs."""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(".").resolve()
TARGET = ROOT / "results" / "predictions" / "a9_junyi_learner_based_dkt_t500_seed42.csv"
NEED = 3_269_022
PARENT = 5840


def nrows(p: Path) -> int:
    if not p.exists():
        return 0
    with p.open("rb") as f:
        return max(sum(1 for _ in f) - 1, 0)


def main():
    print("Watching for complete Junyi DKT t500...", flush=True)
    while nrows(TARGET) < NEED:
        n = nrows(TARGET)
        print(f"  t500 rows={n}/{NEED}", flush=True)
        time.sleep(30)
    print("t500 complete. Stopping old parent if still alive.", flush=True)
    subprocess.run(["taskkill", "/PID", str(PARENT), "/T", "/F"], check=False)
    time.sleep(2)
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    r = subprocess.run(
        [sys.executable, "-u", str(ROOT / "scripts" / "a9_run_five_missing.py")],
        cwd=ROOT,
        env=env,
    )
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
