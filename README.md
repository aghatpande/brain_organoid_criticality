# brain_organoid_criticality
benchmarking organoid eephys data for criticality


Open, reproducible tools for benchmarking and measuring critical-like dynamics in neural population recordings, with an initial focus on brain organoid extracellular electrophysiology.

## Status

Early-stage project with an initial NWB ingestion and spike-time utility layer
in place. The goal is to build an end-to-end open-source workflow for:
- ingesting spike-sorted and/or electrode-level neural recordings
- computing candidate criticality metrics
- benchmarking data sufficiency and quality for those metrics
- generating reproducible figures, reports, and notebooks

Current capabilities include:
- inspecting local NWB files for session metadata, acquisition names, processing modules, and units-table presence
- listing and reading chunks from acquisition-level NWB `ElectricalSeries` objects
- loading NWB `units` spike times into a package-level `SortedSpikes` container
- flattening spike times across units for population-level analysis
- basic spike-time binning for downstream avalanche-style analyses
- validation of the units-based path on one real DANDI asset from Dandiset `000022`

## Planned scope

Initial focus areas include:
- data ingestion and metadata normalization
- preprocessing of extracellular electrophysiology datasets
- avalanche-based analyses
- distance-from-criticality style metrics
- validation and robustness checks
- reproducible benchmark notebooks

## Repository structure

```text
src/        Python package source code
tests/      Unit and integration tests
notebooks/  Exploratory and tutorial notebooks
docs/       Project documentation; roadmap tracked in GitHub milestones/issues
scripts/    Command-line or utility scripts
data/       Data manifests and lightweight metadata only
results/    Generated outputs and summaries
```

## Installation
Clone the repository and install in editable mode:
```bash
git clone https://github.com/YOUR_USERNAME/brain_organoid_criticality.git
cd brain_organoid_criticality
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

For development with NWB support:
```bash
pip install -e ".[dev,nwb]"
```

Run the current checks with:
```bash
pytest
ruff check src/ tests/
mypy src/
```
## Development goals
•	build reusable, documented analysis functions
•	support public benchmark datasets where possible
•	keep workflows transparent and reproducible
•	make outputs useful to both computational neuroscientists and experimental labs

## Contributing

Contributions, suggestions, and issue reports are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on the repository layout, recommended workflow, code style, and outstanding areas of work.

## License
This project is licensed under the Apache License 2.0.
