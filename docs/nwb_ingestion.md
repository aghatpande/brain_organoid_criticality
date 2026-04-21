# NWB Ingestion Layer

## Purpose

This document describes the current NWB-facing ingestion layer for
`brain_organoid_criticality` and the next steps for evolving it into a fuller
upstream subsystem.

The goal of this layer is to give the project a clean entry point for working
with NWB-backed electrophysiology datasets, including DANDI-hosted in vivo
recordings, while keeping downstream criticality analyses independent of PyNWB
internals.

## Current Scope

The current implementation supports local NWB files and provides:

- metadata-first inspection of an NWB file
- discovery of available `ElectricalSeries` objects
- chunked reading of electrical trace data by sample index
- detection of whether an NWB `units` table is present
- extraction of spike times from the NWB `units` table into a package-level
  canonical container

This is intentionally a thin first slice. It is designed to support questions
such as:

- Does this file contain raw electrical traces?
- Does this file already contain sorted units?
- What is the approximate sampling rate, duration, and channel count?
- Can downstream analyses consume archived spike times without depending on
  `pynwb` directly?

## Module Boundaries

The current boundary between modules is:

- `loaders.py`
  Reads NWB files using PyNWB and exposes normalized recording-level summaries
  and electrical-series references.
- `spikes.py`
  Converts NWB `units` tables into the project-level `SortedSpikes` container
  and validates spike-time structure.
- `models.py`
  Defines small dataclasses that downstream code can depend on without needing
  to import PyNWB.
- `avalanches.py`
  Remains downstream analysis code and should consume standardized spike times,
  not raw NWB containers.

Future work should keep this boundary intact. Raw NWB access belongs in the
loader layer. Spike-sorting pipeline integration belongs in a future
`sorting.py`. Criticality analyses should operate on the normalized outputs of
those layers.

## Current Public API

The initial NWB-related API consists of:

- `inspect_nwb(path)`
- `list_electrical_series(path)`
- `get_electrical_series_ref(path, series_name=None)`
- `read_electrical_series_chunk(path, series_name=None, start=0, stop=None)`
- `has_units_table(path)`
- `load_units_from_nwb(path)`
- `flatten_spike_times(sorted_spikes)`
- `validate_sorted_spikes(sorted_spikes)`

The canonical model types are:

- `RecordingSummary`
- `ElectricalSeriesRef`
- `SortedSpikes`

## Design Intent

The important design choice in this layer is that public package code should
not pass around raw `NWBFile` objects. Instead:

1. `loaders.py` uses PyNWB internally.
2. The rest of the package depends on small, stable dataclasses and NumPy
   arrays.
3. Downstream analysis modules remain insulated from file-format details.

This keeps the project adaptable as additional loaders, manifest formats, and
sorting backends are added.

## What This Layer Does Not Do Yet

The current implementation does not yet provide:

- DANDI API integration or remote asset access
- manifest-driven dataset selection
- generalized support for multiple NWB acquisition layouts
- a `sorting.py` layer for running or importing external spike-sorting results
- richer extraction of subject, session, probe, or channel metadata
- benchmark notebooks on real public datasets

Those are expected follow-on tasks rather than omissions in the current scope.

## Tests

Current tests cover:

- spike-container flattening and validation
- a synthetic NWB file with both an `ElectricalSeries` acquisition and a
  `units` table
- inspection, chunked trace reads, and unit extraction from that synthetic file

The focused test command used for this layer was:

```bash
HOME=/Users/asgnxt/brain_organoid_criticality PYNWB_NO_CACHE_DIR=1 .venv/bin/python -m pytest tests
```

## Environment Notes

PyNWB initializes a cache directory during import. In constrained or sandboxed
environments, that cache path may need to be redirected away from the default
user cache location.

For local development in this repository, using a repo-local `HOME` together
with `PYNWB_NO_CACHE_DIR=1` was sufficient to run the current test suite in the
provided sandbox.

## Immediate Follow-up TODOs

The next tasks for this layer should be:

- add DANDI-aware dataset manifests that record dandiset ID, version, and asset
  path
- support remote DANDI asset resolution in addition to local `.nwb` paths
- expand metadata extraction for subjects, probes, channels, and session-level
  provenance
- handle multiple electrical series more explicitly, including clearer
  selection logic
- add tests covering units-only files, raw-only files, and multi-series files
- add a future `sorting.py` adapter layer for external spike-sorting pipelines
- validate this API against one real DANDI dataset such as Allen Visual Coding
  or OpenScope
