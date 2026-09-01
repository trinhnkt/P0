#!/usr/bin/env python3
"""Copy accepted IJIET sources into IJIET_FINAL_REVISION/. Never writes into IJIET_SUBMISSION/."""
from __future__ import annotations

import hashlib
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "IJIET_SUBMISSION"
REV = ROOT / "IJIET_FINAL_REVISION"
HASH_LOG = REV / "audit" / "SETUP_HASHES.txt"

COPIES = [
    (SUB / "source" / "main_ijiet_full.docx", REV / "manuscript" / "main_ijiet_full.docx"),
    (SUB / "source" / "main_ijiet_full.doc", REV / "manuscript" / "main_ijiet_full.doc"),
    (SUB / "output" / "main_ijiet_full.pdf", REV / "output" / "baseline_from_ijiet_submission.pdf"),
    (SUB / "source" / "generate_ijiet_fig1.py", REV / "figures" / "generate_ijiet_fig1.py"),
    (SUB / "tables" / "punchline_ece.csv", REV / "tables" / "punchline_ece.csv"),
    (SUB / "tables" / "compare_published.csv", REV / "tables" / "compare_published.csv"),
    (SUB / "tables" / "table_03_four_partition.tex", REV / "tables" / "table_03_four_partition.tex"),
    (SUB / "tables" / "README.md", REV / "tables" / "README.md"),
    (SUB / "supplementary" / "TABLE_S1_MODEL_SETTINGS.md", REV / "supplementary" / "TABLE_S1_MODEL_SETTINGS.md"),
    (SUB / "audit" / "FINAL_NUMERIC_AUDIT.md", REV / "audit" / "BASELINE_FINAL_NUMERIC_AUDIT.md"),
    (SUB / "audit" / "CLAIM_TO_RESULT_MATRIX.md", REV / "audit" / "BASELINE_CLAIM_TO_RESULT_MATRIX.md"),
    (SUB / "audit" / "REFERENCE_LIVE_AUDIT.md", REV / "audit" / "BASELINE_REFERENCE_LIVE_AUDIT.md"),
    (SUB / "audit" / "ijiet08_fivefold_denominators.csv", REV / "analysis" / "ijiet08_fivefold_denominators.csv"),
    (SUB / "audit" / "ijiet08_seed42_kc_cluster_ci.csv", REV / "analysis" / "ijiet08_seed42_kc_cluster_ci.csv"),
    (SUB / "audit" / "ijiet08_seed42_gate_points.csv", REV / "analysis" / "ijiet08_seed42_gate_points.csv"),
    (SUB / "audit" / "ijiet08_table4_from_threshold_rates.csv", REV / "analysis" / "ijiet08_table4_from_threshold_rates.csv"),
    (ROOT / "analysis" / "four_partition" / "punchline_ece.csv", REV / "analysis" / "four_partition_punchline_ece.csv"),
    (ROOT / "analysis" / "four_partition" / "summary_4part_bucket.csv", REV / "analysis" / "summary_4part_bucket.csv"),
    (ROOT / "analysis" / "direction_c" / "c2_fivefold_verdict.txt", REV / "analysis" / "c2_fivefold_verdict.txt"),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    for name in ("manuscript", "analysis", "audit", "supplementary", "figures", "tables", "output"):
        (REV / name).mkdir(parents=True, exist_ok=True)

    before = {}
    lines = ["# Hashes of originals (must be unchanged after copy)\n"]
    for src, dst in COPIES:
        if not src.exists():
            lines.append(f"MISSING_SRC {src}\n")
            continue
        before[str(src)] = sha256(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        lines.append(f"COPIED {src} -> {dst}\n")
        lines.append(f"  src_sha256={before[str(src)]}\n")
        lines.append(f"  dst_sha256={sha256(dst)}\n")

    after_ok = True
    for src, _ in COPIES:
        if not src.exists():
            continue
        now = sha256(src)
        if now != before[str(src)]:
            after_ok = False
            lines.append(f"MUTATED_ORIGINAL {src}\n")
    lines.append(f"ORIGINALS_UNCHANGED={after_ok}\n")
    HASH_LOG.write_text("".join(lines), encoding="utf-8")
    print(HASH_LOG.read_text(encoding="utf-8"))
    if not after_ok:
        raise SystemExit("originals were mutated")


if __name__ == "__main__":
    main()
