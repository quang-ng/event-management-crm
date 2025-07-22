import os
import sys

import pytest

HELP = """
Usage: python run_test.py [options]

Options:
  --cov           Enable coverage reporting (requires pytest-cov)
  -v, --verbose   Increase verbosity
  --help          Show this help message
  [other args]    Any other pytest arguments
"""
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def main():
    args = ["."]
    user_args = sys.argv[1:]
    if "--help" in user_args:
        print(HELP)
        sys.exit(0)
    if "--cov" in user_args:
        args = ["--cov=.", "--cov-report=term-missing"] + args
        user_args.remove("--cov")
    if "-v" in user_args or "--verbose" in user_args:
        args.insert(0, "-v")
        if "-v" in user_args:
            user_args.remove("-v")
        if "--verbose" in user_args:
            user_args.remove("--verbose")
    # Pass any remaining args through
    args += user_args
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 