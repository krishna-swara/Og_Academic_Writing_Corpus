"""Command-line entry point."""
from __future__ import annotations

import argparse
import json
import sys

from .acquire import acquire_pararev, acquire_pararev_full
from .acquire_auxiliary import acquire_acl_catalog, acquire_jfleg
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
    acquire_full = sub.add_parser("acquire-pararev-full", help="download and normalize ParaRev full corpus locally")
    acquire_full.add_argument("--accept-license", action="store_true", help="acknowledge CC BY-NC-SA 4.0 non-commercial, attribution, and share-alike terms")
    acquire_full.add_argument("--raw-dir", default="raw_sources/pararev")
    acquire_full.add_argument("--output", default="processed/pararev_full_pairs.jsonl")
    acquire_jfleg_cmd = sub.add_parser("acquire-jfleg", help="download JFLEG as a separate sentence-level auxiliary benchmark")
    acquire_jfleg_cmd.add_argument("--accept-license", action="store_true", help="acknowledge CC BY-NC-SA 4.0 terms")
    acquire_jfleg_cmd.add_argument("--raw-dir", default="raw_sources/jfleg")
    acquire_jfleg_cmd.add_argument("--output", default="processed/jfleg_aux_pairs.jsonl")
    acquire_acl = sub.add_parser("acquire-acl-catalog", help="download ACL Anthology bibliographic metadata only")
    acquire_acl.add_argument("--raw-dir", default="raw_sources/acl_anthology")
    acquire_acl.add_argument("--output", default="processed/acl_anthology_metadata.jsonl")
    batch = sub.add_parser("acquire-batch", help="acquire ParaRev full, JFLEG, and ACL metadata in one run")
    batch.add_argument("--accept-license", action="store_true", help="acknowledge CC BY-NC-SA 4.0 terms for ParaRev and JFLEG")
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
    elif args.command == "acquire-pararev-full":
        try:
            manifest = acquire_pararev_full(args.output, args.raw_dir, accept_license=args.accept_license)
        except (ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print(json.dumps(manifest, indent=2))
    elif args.command == "acquire-jfleg":
        try:
            manifest = acquire_jfleg(args.output, args.raw_dir, accept_license=args.accept_license)
        except (ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print(json.dumps(manifest, indent=2))
    elif args.command == "acquire-acl-catalog":
        try:
            manifest = acquire_acl_catalog(args.output, args.raw_dir)
        except (ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print(json.dumps(manifest, indent=2))
    elif args.command == "acquire-batch":
        try:
            results = {
                "pararev_full": acquire_pararev_full(
                    "processed/pararev_full_pairs.jsonl",
                    "raw_sources/pararev",
                    accept_license=args.accept_license,
                ),
                "jfleg": acquire_jfleg(
                    "processed/jfleg_aux_pairs.jsonl",
                    "raw_sources/jfleg",
                    accept_license=args.accept_license,
                ),
                "acl_anthology_metadata": acquire_acl_catalog(
                    "processed/acl_anthology_metadata.jsonl",
                    "raw_sources/acl_anthology",
                ),
            }
        except (ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print(json.dumps(results, indent=2))
    elif args.command == "acquire-pararev":
        try:
            manifest = acquire_pararev(args.output, args.raw_dir, accept_license=args.accept_license)
        except (ValueError, OSError) as exc:
            print(str(exc), file=sys.stderr)
            raise SystemExit(1) from exc
        print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
