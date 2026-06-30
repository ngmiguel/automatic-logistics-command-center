#!/usr/bin/env bash
set -euo pipefail
exec python scripts/tests/run_module.py worker "$@"
