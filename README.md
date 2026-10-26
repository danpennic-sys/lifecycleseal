# LifecycleSeal

**Local-first full job lifecycle evidence bundler and QuantumGuard sealer for field operators.**

Offline. Deterministic. Pay once. Compatible with QuantumGuard CONTRACT-v1, VeriQuote, FieldSeal, JobSeal, CloseSeal, Evidence-Core, and Chaser.

## Why LifecycleSeal?

Field operators need one verifiable pack that proves the entire job: quote accepted, work performed and logged, close-out signed, invoice issued. LifecycleSeal aggregates the individual sealed packs into a single client-verifiable QuantumGuard evidence bundle.

- No SaaS. No subscription. Runs completely offline after key setup.
- Clients (or their auditors) verify the master pack with the free QuantumGuard verifier.
- Pairs with the full Operator Pages suite.
- Exports simple summary CSVs and printable HTML bundles.

## Quick Start

```bash
# Optional but recommended for real Ed25519 signatures
pip install cryptography

python3 src/lifecycleseal.py --demo
python3 src/lifecycleseal.py --data samples/lifecycle-001.json --out sealed_lifecycle.json
```

Verify the output with the QuantumGuard CLI:

```bash
qg verify sealed_lifecycle.json
```

Expected verdict: PASS (when using real cryptography).

## What you can sell

| SKU       | Price | Includes                                      |
|-----------|-------|-----------------------------------------------|
| Operator  | $79   | CLI + HTML bundler + key setup guide + 1-year email support |
| Command   | $199  | + batch mode + templates + reseller rights for client packs |
| Agency    | $499  | + white-label HTML + design partner onboarding |

Purchase / access: danpennic@gmail.com

Source remains free under Apache-2.0 OR MIT. Commercial Operator Pack sold separately.

## Stack Fit

- Python CLI (same family as VeriQuote, FieldSeal, JobSeal, CloseSeal)
- Emits QuantumGuard CONTRACT-v1 bundles (Ed25519, deterministic hashing)
- Local key storage (PEM)
- Ready for Chaser and Operator App integration

## License

Apache-2.0 OR MIT
