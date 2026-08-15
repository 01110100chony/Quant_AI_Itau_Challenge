# RSR_001 post-OOS forensic preflight

Classification: `POST_OOS_FORENSIC_AUDIT`

Run date: 2026-08-15 (America/Sao_Paulo)

Audit branch base: `9660319d0da25767f1be8b1240de9653893bd2e8`

## Scope and guardrails

This audit reproduces an already-consumed OOS. It cannot restore a virgin
holdout, rescue `RSR_001`, or promote any parameter. H1 and H2 remain
immutable. No market data were downloaded. Canonical experiment metadata are
not changed by this audit.

An unrelated untracked file,
`Quant_AI_Itau_Challenge-relatorio-epsilon.rar`, appeared after switching from
the local CM_001 line to the audited branch. It does not overlap RSR_001 code,
data, tests, specification, manifest, decision, results, or reports and is
preserved untouched.

## Commit-chain checks

- H1: `66bd72831eb803beeeefe63686ef915385f00b0c`
- H2: `a45b3a4b272c65a80170ad3e5db0dd8bb75e3f5b`
- Audited HEAD: `9660319d0da25767f1be8b1240de9653893bd2e8`
- `git merge-base --is-ancestor H1 H2`: PASS
- `git merge-base --is-ancestor H2 HEAD`: PASS
- `d62ea1a..H1`: only `research/experiments/RSR_001/decision.md`
- `H1..H2`: only `contexts/research/experiment_registry.md` and
  `research/experiments/RSR_001/manifest.toml`
- `H2..HEAD`: exactly ten added notes under `Quant_Documents/`

## Frozen Git-blob hashes

| Input | Expected and observed SHA-256 | Result |
|---|---|---|
| `data/raw/us_sector_etfs_plus_spy_adjusted_close.csv` | `30bf7c3e6834e4eae29731be64d186d500826f9751c26fbf54c83b2856e8b177` | PASS |
| `scripts/rsr_001.py` | `9d9595660df5bc154354bc8cb4ddc9c37129331495bff8deaa80ea7c1098bfb3` | PASS |
| `research/experiments/RSR_001/spec.md` | `d0796279e743e8fe1030d33fbc17c07d5f1d9ae18e98f3ee0be8292ccfd05467` | PASS |
| `requirements.txt` | `d5303276ad646333897abf6e8ce84c8cbb6fa60a7b92c6547162c2cc84e1473b` | PASS |

The repository has `core.autocrlf=true`, so hashes of the checked-out Windows
working files differ from the canonical Git blobs. The detached H2 reproduction
must therefore be created with `core.autocrlf=false`; its on-disk hashes must
match the table before execution.

## Baseline verification

- Python: `3.14.3` (project contract is Python 3.11+)
- `python -B -m unittest discover -s tests -p "test*.py"`: PASS, 4 tests
- `python -B scripts/verify_research.py`: PASS (13 context pages, 8 registry
  entries, 2 manifests)
- `git diff --check`: PASS

## Canonical-state conflicts at audited HEAD

- Vault notes state that OOS was opened and produced `NO_GO`.
- `manifest.toml` says `FROZEN` and `oos_opened = false`.
- Registry says `FROZEN` and OOS `CLOSED`.
- `decision.md` says `RESEARCH` and OOS closed.
- `results.md` says Final OOS was not executed.
- Canonical terminal transcript, execution receipt, raw OOS CSV, and verdict
  CSV are absent.

These conflicts are recorded, not reconciled. Canonical files remain untouched
until a later human decision.
