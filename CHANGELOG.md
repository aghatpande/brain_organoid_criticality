# Changelog

## Unreleased

### Added

- Added NWB-facing data models for recording summaries, electrical series references, and canonical sorted spike times.
- Added initial NWB loading utilities for inspecting local `.nwb` files, listing electrical series, checking for a units table, and reading electrical data chunks.
- Added spike extraction utilities to load spike times from an NWB `units` table, validate the resulting container, and flatten spike times across units.
- Added a small inspection script at `scripts/inspect_nwb.py` for manually summarizing an NWB file from the command line.
- Added optional `nwb` dependencies in `pyproject.toml` via `pynwb`.
- Added initial tests for spike container validation and a synthetic NWB round-trip covering raw traces plus sorted units.
