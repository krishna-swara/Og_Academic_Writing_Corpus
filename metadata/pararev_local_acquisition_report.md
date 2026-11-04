# ParaRev local acquisition report

## Reported local run

The repository owner reported completing the following commands in a local clone:

```bash
og-awc acquire-pararev --accept-license
og-awc validate --input processed/pararev_pairs.jsonl
og-awc prepare --input processed/pararev_pairs.jsonl --output-dir processed/pararev_splits
```

Reported outcome:
- ParaRev manually annotated subset acquired: 641 paragraph pairs.
- Validation completed successfully.
- Deterministic split output:
  - train: 452 records
  - validation: 44 records
  - test: 145 records
  - duplicates: 0 records

These are owner-reported local results. They have not been independently verified in this GitHub repository or CI. The raw and processed dataset files are not included in this commit.

## TLS / SSL security note

The local troubleshooting reportedly involved disabling TLS certificate verification to work around an SSL error. **Do not retain or use that workaround.** Disabling certificate verification makes HTTPS downloads vulnerable to interception and can allow an untrusted dataset file to be accepted as authentic.

Restore normal certificate verification in `src/og_awc/acquire.py` and use a trusted CA bundle / correctly configured system certificates (for example, update the OS certificate store or configure `SSL_CERT_FILE` to a trusted CA bundle). Do not use `ssl._create_unverified_context()`, `CERT_NONE`, or equivalent insecure settings.

After restoring verification, re-run acquisition and compare the downloaded file's SHA-256 with the manifest. Keep the pinned upstream revision and record the final verified checksum.

## Publication status

This report documents local processing only. It does not grant permission to redistribute ParaRev or underlying article text. Keep downloaded text out of public GitHub until the relevant dataset and underlying-document rights have been reviewed. Preserve required attribution and share-alike notices for any permitted redistribution.
