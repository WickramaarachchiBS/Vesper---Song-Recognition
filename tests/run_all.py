"""Run all test scripts and print their outputs.

This file is intended to be executed as `python tests/run_all.py` and will
call the individual test runners. It does not require pytest.
"""
import subprocess
import sys
import os


def run_script(rel_path):
    path = os.path.join(os.path.dirname(__file__), rel_path)
    print("\n" + "#" * 60)
    print(f"Running: {rel_path}")
    print("#" * 60)
    # Use same python interpreter
    cmd = [sys.executable, path]
    proc = subprocess.run(cmd, capture_output=False)
    print(f"Exit code: {proc.returncode}")


def main():
    scripts = [
        "../test_system.py",       # existing system test
        "unit_tests.py",
        "integration_tests.py",
        "performance_tests.py",
        "accuracy_tests.py",
        "uat_checks.py",
    ]

    for s in scripts:
        run_script(s)


if __name__ == '__main__':
    main()
