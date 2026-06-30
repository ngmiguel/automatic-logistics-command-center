#!/usr/bin/env python3
"""Run tests for a specific ALCC module.

Usage:
    python scripts/tests/run_module.py auth
    python scripts/tests/run_module.py all
    python scripts/tests/run_module.py all --cov
"""

import subprocess
import sys

MODULES = [
    "shared",
    "auth",
    "fleet",
    "routing",
    "tracking",
    "notification",
    "analytics",
    "simulator",
    "worker",
    "integration",
]


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <module|all> [--cov]")
        print(f"Modules: {', '.join(MODULES)}")
        return 1

    module = sys.argv[1]
    with_cov = "--cov" in sys.argv

    if module == "all":
        paths = [f"tests/{m}/" for m in MODULES]
    elif module in MODULES:
        paths = [f"tests/{module}/"]
    else:
        print(f"Unknown module: {module}")
        return 1

    cmd = ["pytest", *paths, "-v", "--tb=short"]
    if with_cov:
        cmd.extend(["--cov=alcc", "--cov-report=term-missing"])

    print(f"Running: {' '.join(cmd)}")
    return subprocess.call(cmd)


if __name__ == "__main__":
    sys.exit(main())
