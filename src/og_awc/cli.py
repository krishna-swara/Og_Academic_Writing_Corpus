"""Command-line entry point."""
from __future__ import annotations

import argparse
import sys

from .validation import validate_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(prog="og-awc", description="Validate Og-AWC JSONL corpus files")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a JSONL file")
    validate.add_argument("--input", required=True)
    args = parser.parse_args()
    if args.command == "validate":
        errors = validate_jsonl(args.input)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            raise SystemExit(1)
        print(f"Validation passed: {args.input}")


if __name__ == "__main__":
    main()
