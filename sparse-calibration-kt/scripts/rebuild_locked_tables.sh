#!/usr/bin/env bash
# Rebuild SI Tables S8–S9 and verify locked ASSISTments T-KT ECE.
# Does not retrain. Does not overwrite Table 5 cells 0.1136 / 0.2280.
set -e
cd "$(dirname "$0")/.."
export PYTHONPATH="."
python scripts/p0_rebuild_locked_tables.py
echo "Frozen-table rebuild complete. Retrain path remains scripts/reproduce_one_dataset.sh"
