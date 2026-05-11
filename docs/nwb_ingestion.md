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

## Real DANDI Validation

The local-file ingestion path has been validated against one real DANDI NWB
asset:

- Dandiset: `000022`
- Version: `0.251116.2247`
- Asset path: `sub-744912845/sub-744912845_ses-766640955.nwb`
- Asset ID: `ac4bfefc-d259-4d13-a083-89df1f9044b9`

The asset was downloaded locally and inspected with `scripts/inspect_nwb.py`.
The current loader successfully extracted session metadata and detected the
NWB `units` table:

- `session_id='766640955'`
- `subject_id='744912845'`
- `has_units=True`
- `has_raw_electrical_series=False`

This file does not expose raw extracellular `ElectricalSeries` objects in
`acquisition`; the acquisition entries are running-wheel signals. That means
raw-trace discovery remains layout-dependent, but the units-based path works on
this real public asset.

A minimal downstream spike pipeline also succeeded:

```python
spikes = load_units_from_nwb(path)
population_spikes = flatten_spike_times(spikes)
counts, edges = bin_spike_times(population_spikes, bin_size=0.01)
```

Observed output:

- `n_units: 2890`
- `t_start_s: 0.0`
- `t_stop_s: 9807.04919153599`
- `n_population_spikes: 124754105`
- `n_bins: 980334`
- `first_10_counts: [40 37 60 77 97 68 52 44 50 40]`

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
