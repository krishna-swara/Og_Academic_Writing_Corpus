"""Command-line entry point."""
from __future__ import annotations

import argparse
import json
import sys

from .acquire import acquire_pararev, acquire_pararev_full
from .pipeline import prepare_dataset
from .validation import validate_jsonl


def main() -> None:
    parser = argparse.ArgumentParser(prog="og-awc", description="Acquire, prepare, and validate Og-AWC JSONL corpus files")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="validate a JSONL file")
    validate.add_argument("--input", required=True)
    prepare = sub.add_parser("prepare", help="deduplicate and create paper-level local splits")
    prepare.add_argument("--input", required=True)
    prepare.add_argument("--output-dir", required=True)
    prepare.add_argument("--seed", default="og-awc-v1")
    acquire = sub.add_parser("acquire-pararev", help="download and normalize ParaRev's annotated subset locally")
    acquire.add_argument("--accept-license", action="store_true", help="acknowledge CC BY-NC-SA 4.0 non-commercial, attribution, and share-alike terms")
    acquire.add_argument("--raw-dir", default="raw_sources/pararev")
    acquire.add_argument("--output", default="processed/pararev_pairs.jsonl")
    acquire_full = sub.add_parser("acquire-pararev-full", help="download and normalize ParaRev full corpus locally")\n    acquire_full.add_argument("--accept-license", action="store_true", help="acknowledge CC BY-NC-SA 4.0 non-commercial, attribution, and share-alike terms")\n    acquire_full.add_argument("--raw-dir", default="raw_sources/pararev")\n    acquire_full.add_argument("--output", default="processed/pararev_full_pairs.jsonl")\n    args = parser.parse_args()
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
    elif args.command == "acquire-pararev-full":\n        try:\n            manifest = acquire_pararev_full(args.output, args.raw_dir, accept_license=args.accept_license)\n        except (ValueError, OSError) as exc:\n            print(str(exc), file=sys.stderr)\n            raise SystemExit(1) from exc\n        print(json.dumps(manifest, indent=2))\n    elif args.command == "acquire-pararev":
        try:
            manifest = acquire_pararev(args.output, args.raw_dir, accept_license=args.accept_license)
        except (ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
