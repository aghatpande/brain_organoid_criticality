# Changelog

## Unreleased

### Added

- Added `check_sufficiency()` (in `quality.py`) returning a `SufficiencyReport` that scores a recording's unit count, duration, mean firing rate, and bin count against configurable thresholds, accumulating human-readable warnings and failures.
- Added `branching_ratio()` (in `metrics.py`), the Wilting & Priesemann multistep-regression estimator of the branching ratio sigma, robust to spatial subsampling.
- Added `distance_to_criticality()` (in `metrics.py`) computing `DCC = 1 - sigma` with a moving-block bootstrap confidence interval, refusing a point estimate when data sufficiency fails.
- Added the `SufficiencyReport`, `BranchingRatioEstimate`, and `DCCResult` data models, exported from the package public API.
- Added pytest configuration so the test suite runs from the repository root.
- Added a `dev` optional dependency group with pytest, pytest-cov, Ruff, and mypy.
- Added mypy configuration for the current source tree and untyped third-party imports.
- Added NWB-facing data models for recording summaries, electrical series references, and canonical sorted spike times.
- Added initial NWB loading utilities for inspecting local `.nwb` files, listing electrical series, checking for a units table, and reading electrical data chunks.
- Added spike extraction utilities to load spike times from an NWB `units` table, validate the resulting container, and flatten spike times across units.
- Added a small inspection script at `scripts/inspect_nwb.py` for manually summarizing an NWB file from the command line.
- Added optional `nwb` dependencies in `pyproject.toml` via `pynwb`.
- Added initial tests for spike container validation and a synthetic NWB round-trip covering raw traces plus sorted units.
- Added GitHub Actions CI for pull requests and pushes to `main`, running pytest, Ruff, and mypy.

### Documentation

- Documented validation of the NWB ingestion path on a real DANDI `000022` asset.
- Updated README project status and contributor setup instructions to reflect the current NWB and development-tooling support.
