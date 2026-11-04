"""Command-line entry point."""
from __future__ import annotations

import argparse
import sys

from .pipeline import prepare_dataset
from .validation import validate_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(prog="og-awc", description="Prepare and validate Og-AWC JSONL corpus files")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a JSONL file")
    validate.add_argument("--input", required=True)
    prepare = sub.add_parser("prepare", help="deduplicate and create paper-level local splits")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument("--seed", default="og-awc-v1")
    args = parser.parse_args()
    if args.command == "validate":
        errors = validate_jsonl(args.input)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            raise SystemExit(1)
        print(f"Validation passed: {args.input}")
    elif args.command == "prepare":
        try:
            report = prepare_dataset(args.input, args.output_dir, seed=args.seed)
        except (ValueError, RuntimeError) as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print("\n".join(f"{key}: {value}" for key, value in report.items()))


if __name__ == "__main__":
    main()
